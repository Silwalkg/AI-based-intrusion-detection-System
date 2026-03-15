"""
Data preprocessing module for IDS
Handles NSL-KDD and CIC-IDS2017 datasets, with support for combining both.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import os
import glob

# Shared feature set used when combining both datasets.
# These are semantically equivalent features present in both NSL-KDD and CIC-IDS2017.
COMMON_FEATURES = [
    'duration', 'src_bytes', 'dst_bytes', 'count',
    'serror_rate', 'rerror_rate', 'same_srv_rate', 'diff_srv_rate',
    'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate', 'dst_host_serror_rate', 'dst_host_rerror_rate',
]

# CIC-IDS2017 CSV/parquet column name → COMMON_FEATURES name mapping
CIC_COLUMN_MAP = {
    'Flow Duration':              'duration',
    'Total Fwd Packets':          'count',
    'Total Backward Packets':     'dst_host_count',
    'Total Length of Fwd Packets':'src_bytes',
    'Total Length of Bwd Packets':'dst_bytes',
    'Fwd Packet Length Max':      'dst_host_srv_count',
    'Flow Packets/s':             'same_srv_rate',
    'Flow Bytes/s':               'diff_srv_rate',
    'Fwd IAT Mean':               'serror_rate',
    'Bwd IAT Mean':               'rerror_rate',
    'Fwd Header Length':          'dst_host_same_srv_rate',
    'Bwd Header Length':          'dst_host_diff_srv_rate',
    'SYN Flag Count':             'dst_host_serror_rate',
    'RST Flag Count':             'dst_host_rerror_rate',
}
# CIC-IDS2017 label → unified attack category
CIC_LABEL_MAP = {
    'benign':                  'normal',
    'normal':                  'normal',
    'dos hulk':                'dos',
    'dos goldeneye':           'dos',
    'dos slowloris':           'dos',
    'dos slowhttptest':        'dos',
    'ddos':                    'dos',
    'heartbleed':              'dos',
    'portscan':                'probe',
    'bot':                     'r2l',
    'ftp-patator':             'r2l',
    'ssh-patator':             'r2l',
    'web attack – brute force':'r2l',
    'web attack – xss':        'r2l',
    'web attack – sql injection': 'u2r',
    'infiltration':            'u2r',
}


class DataPreprocessor:
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_names = COMMON_FEATURES

    # ------------------------------------------------------------------
    # NSL-KDD
    # ------------------------------------------------------------------
    def load_nsl_kdd(self, train_path='data/KDDTrain+.txt', test_path='data/KDDTest+.txt'):
        """Load NSL-KDD dataset and return unified DataFrames."""
        column_names = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
            'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
            'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
            'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
            'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty'
        ]
        print("Loading NSL-KDD dataset...")
        train_df = pd.read_csv(train_path, names=column_names, header=None)
        test_df  = pd.read_csv(test_path,  names=column_names, header=None)
        train_df = train_df.drop('difficulty', axis=1)
        test_df  = test_df.drop('difficulty',  axis=1)
        print(f"  ✓ NSL-KDD — Train: {len(train_df):,}  Test: {len(test_df):,}")
        return train_df, test_df

    def _nsl_kdd_to_unified(self, df):
        """Map NSL-KDD DataFrame to unified schema (COMMON_FEATURES + label)."""
        df = df.copy()
        df['label'] = df['label'].apply(self._categorize_nsl_label)
        unified = df[COMMON_FEATURES + ['label']].copy()
        # Ensure numeric
        for col in COMMON_FEATURES:
            unified[col] = pd.to_numeric(unified[col], errors='coerce').fillna(0)
        return unified

    def _categorize_nsl_label(self, label):
        dos_attacks   = ['back','land','neptune','pod','smurf','teardrop','apache2','udpstorm','processtable','worm']
        probe_attacks = ['satan','ipsweep','nmap','portsweep','mscan','saint']
        r2l_attacks   = ['guess_passwd','ftp_write','imap','phf','multihop','warezmaster','warezclient',
                         'spy','xlock','xsnoop','snmpguess','snmpgetattack','httptunnel','sendmail','named']
        u2r_attacks   = ['buffer_overflow','loadmodule','rootkit','perl','sqlattack','xterm','ps']
        label = label.strip().lower()
        if label == 'normal':           return 'normal'
        if any(a in label for a in dos_attacks):   return 'dos'
        if any(a in label for a in probe_attacks): return 'probe'
        if any(a in label for a in r2l_attacks):   return 'r2l'
        if any(a in label for a in u2r_attacks):   return 'u2r'
        return 'dos'

    # ------------------------------------------------------------------
    # CIC-IDS2017
    # ------------------------------------------------------------------
    def load_cic_ids2017(self, data_dir='data/CIC-IDS2017'):
        """
        Load CIC-IDS2017 from data_dir.
        Supports:
          - parquet file downloaded via nids-datasets package (CIC_Flow.parquet)
          - CSV files downloaded manually from Kaggle
        Returns a single unified DataFrame.
        """
        parquet_file = os.path.join(data_dir, 'Network-Flows', 'CICIDS_Flow.parquet')
        # nids-datasets creates an extra subfolder when downloaded into data/CIC-IDS2017
        parquet_nested = os.path.join(data_dir, 'CIC-IDS2017', 'Network-Flows', 'CICIDS_Flow.parquet')
        # Also check flat parquet location
        parquet_flat = os.path.join(data_dir, 'CICIDS_Flow.parquet')

        csv_files = glob.glob(os.path.join(data_dir, '*.csv'))

        if os.path.exists(parquet_file) or os.path.exists(parquet_flat) or os.path.exists(parquet_nested):
            path = next(p for p in [parquet_file, parquet_nested, parquet_flat] if os.path.exists(p))
            print(f"Loading CIC-IDS2017 from parquet: {path}")
            df = pd.read_parquet(path)
            df.columns = df.columns.str.strip()
            print(f"  ✓ CIC-IDS2017: {len(df):,} rows")
            return df

        elif csv_files:
            print(f"Loading CIC-IDS2017 from {len(csv_files)} CSV file(s)...")
            frames = []
            for f in sorted(csv_files):
                try:
                    chunk = pd.read_csv(f, encoding='utf-8', low_memory=False)
                    frames.append(chunk)
                    print(f"  ✓ {os.path.basename(f)}: {len(chunk):,} rows")
                except Exception as e:
                    print(f"  ⚠ Skipping {os.path.basename(f)}: {e}")
            df = pd.concat(frames, ignore_index=True)
            df.columns = df.columns.str.strip()
            print(f"  ✓ CIC-IDS2017 total: {len(df):,} rows")
            return df

        else:
            raise FileNotFoundError(
                f"CIC-IDS2017 not found in '{data_dir}'.\n"
                "Run: python download_dataset.py"
            )

    def _cic_to_unified(self, df):
        """Map CIC-IDS2017 DataFrame to unified schema."""
        df = df.copy()

        # Find label column — parquet uses 'attack_label', CSVs use 'Label'
        label_col = next(
            (c for c in df.columns if c.strip().lower() in ('label', 'attack_label', 'attack_type', 'class')), None
        )
        if label_col is None:
            raise ValueError("CIC-IDS2017: label column not found.")

        # The parquet from nids-datasets uses original CSV-style column names
        # so always use CIC_COLUMN_MAP (not the snake_case parquet map)
        rename = {k: v for k, v in CIC_COLUMN_MAP.items() if k in df.columns}
        df = df.rename(columns=rename)

        # Map labels to unified categories
        df['label'] = df[label_col].astype(str).str.strip().str.lower().map(
            lambda x: next((v for k, v in CIC_LABEL_MAP.items() if k in x), 'dos')
        )

        # Build unified feature DataFrame
        available = [f for f in COMMON_FEATURES if f in df.columns]
        missing   = [f for f in COMMON_FEATURES if f not in df.columns]
        if missing:
            print(f"  ⚠ CIC-IDS2017 missing features (zero-filled): {missing}")

        unified = pd.DataFrame(0.0, index=df.index, columns=COMMON_FEATURES)
        for col in available:
            unified[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        unified['label'] = df['label'].values

        unified.replace([np.inf, -np.inf], np.nan, inplace=True)
        unified.dropna(inplace=True)
        return unified

    # ------------------------------------------------------------------
    # Combine
    # ------------------------------------------------------------------
    def load_combined(self,
                      nsl_train='data/KDDTrain+.txt',
                      nsl_test='data/KDDTest+.txt',
                      cic_dir='data/CIC-IDS2017'):
        """
        Load both datasets, convert to unified schema, and combine.
        Returns (train_df, test_df) with 80/20 stratified split.
        """
        frames = []

        # NSL-KDD
        nsl_train_df, nsl_test_df = self.load_nsl_kdd(nsl_train, nsl_test)
        nsl_all = pd.concat([nsl_train_df, nsl_test_df], ignore_index=True)
        nsl_unified = self._nsl_kdd_to_unified(nsl_all)
        frames.append(nsl_unified)
        print(f"  ✓ NSL-KDD unified: {len(nsl_unified):,} samples")

        # CIC-IDS2017 (optional — skip if not present)
        parquet_exists = (
            os.path.exists(os.path.join(cic_dir, 'Network-Flows', 'CICIDS_Flow.parquet')) or
            os.path.exists(os.path.join(cic_dir, 'CICIDS_Flow.parquet')) or
            os.path.exists(os.path.join(cic_dir, 'CIC-IDS2017', 'Network-Flows', 'CICIDS_Flow.parquet'))
        )
        csv_exists = os.path.isdir(cic_dir) and bool(glob.glob(os.path.join(cic_dir, '*.csv')))

        if parquet_exists or csv_exists:
            cic_raw = self.load_cic_ids2017(cic_dir)
            cic_unified = self._cic_to_unified(cic_raw)
            frames.append(cic_unified)
            print(f"  ✓ CIC-IDS2017 unified: {len(cic_unified):,} samples")
        else:
            print(f"  ⚠ CIC-IDS2017 not found at '{cic_dir}' — training on NSL-KDD only.")
            print(f"     To add it: run python download_dataset.py")

        combined = pd.concat(frames, ignore_index=True).sample(frac=1, random_state=42)
        print(f"\n  ✓ Combined dataset: {len(combined):,} samples")
        print(f"  ✓ Label distribution:\n{combined['label'].value_counts().to_string()}")

        # Stratified 80/20 split
        train_df, test_df = train_test_split(
            combined, test_size=0.2, random_state=42, stratify=combined['label']
        )
        print(f"  ✓ Train: {len(train_df):,}  Test: {len(test_df):,}")
        return train_df, test_df

    # ------------------------------------------------------------------
    # Preprocessing (shared)
    # ------------------------------------------------------------------
    def preprocess_data(self, df, is_training=True):
        """Scale features and encode labels from a unified DataFrame."""
        print("Preprocessing data...")
        X = df[COMMON_FEATURES].values.astype(np.float32)
        y = df['label'].values

        if is_training:
            X_scaled = self.scaler.fit_transform(X)
            y_encoded = self.label_encoder.fit_transform(y)
        else:
            X_scaled = self.scaler.transform(X)
            # Handle unseen labels gracefully
            known = set(self.label_encoder.classes_)
            y_safe = np.array([lbl if lbl in known else self.label_encoder.classes_[0] for lbl in y])
            y_encoded = self.label_encoder.transform(y_safe)

        print(f"  ✓ Features: {X_scaled.shape[1]}  Samples: {X_scaled.shape[0]}")
        print(f"  ✓ Classes: {list(self.label_encoder.classes_)}")
        return X_scaled, y_encoded, y

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------
    def save_preprocessor(self, filepath='models/preprocessor.pkl'):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'feature_names': self.feature_names
            }, f)
        print(f"✓ Preprocessor saved: {filepath}")

    def load_preprocessor(self, filepath='models/preprocessor.pkl'):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.scaler        = data['scaler']
        self.label_encoder = data['label_encoder']
        self.feature_names = data['feature_names']
        print(f"✓ Preprocessor loaded: {filepath}")
