"""
Data preprocessing module for IDS
Handles NSL-KDD and CIC-IDS2017 datasets
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import os

class DataPreprocessor:
    def __init__(self, dataset_type='nsl-kdd'):
        self.dataset_type = dataset_type
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def load_nsl_kdd(self, train_path='data/KDDTrain+.txt', test_path='data/KDDTest+.txt'):
        """Load NSL-KDD dataset"""
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
        test_df = pd.read_csv(test_path, names=column_names, header=None)
        
        # Drop difficulty column
        train_df = train_df.drop('difficulty', axis=1)
        test_df = test_df.drop('difficulty', axis=1)
        
        print(f"✓ Train samples: {len(train_df)}, Test samples: {len(test_df)}")
        return train_df, test_df
    
    def categorize_attacks(self, label):
        """Categorize attacks into main types"""
        dos_attacks = ['back', 'land', 'neptune', 'pod', 'smurf', 'teardrop', 'apache2', 'udpstorm', 'processtable', 'worm']
        probe_attacks = ['satan', 'ipsweep', 'nmap', 'portsweep', 'mscan', 'saint']
        r2l_attacks = ['guess_passwd', 'ftp_write', 'imap', 'phf', 'multihop', 'warezmaster', 'warezclient', 'spy', 'xlock', 'xsnoop', 'snmpguess', 'snmpgetattack', 'httptunnel', 'sendmail', 'named']
        u2r_attacks = ['buffer_overflow', 'loadmodule', 'rootkit', 'perl', 'sqlattack', 'xterm', 'ps']
        
        label = label.strip().lower()
        if label == 'normal':
            return 'normal'
        elif any(attack in label for attack in dos_attacks):
            return 'dos'
        elif any(attack in label for attack in probe_attacks):
            return 'probe'
        elif any(attack in label for attack in r2l_attacks):
            return 'r2l'
        elif any(attack in label for attack in u2r_attacks):
            return 'u2r'
        else:
            return 'dos'  # Default to dos for unknown attacks
    
    def preprocess_data(self, df, is_training=True):
        """Preprocess the dataset"""
        print("Preprocessing data...")
        
        # Categorize attacks
        df['attack_category'] = df['label'].apply(self.categorize_attacks)
        
        # Separate features and labels
        X = df.drop(['label', 'attack_category'], axis=1)
        y = df['attack_category']
        
        # Encode categorical features
        categorical_cols = X.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
        
        # Store feature names
        if is_training:
            self.feature_names = X.columns.tolist()
        
        # Scale numerical features
        if is_training:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        # Encode labels
        if is_training:
            y_encoded = self.label_encoder.fit_transform(y)
        else:
            y_encoded = self.label_encoder.transform(y)
        
        print(f"✓ Features: {X_scaled.shape[1]}, Samples: {X_scaled.shape[0]}")
        print(f"✓ Attack categories: {np.unique(y)}")
        
        return X_scaled, y_encoded, y
    
    def save_preprocessor(self, filepath='models/preprocessor.pkl'):
        """Save preprocessor objects"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'feature_names': self.feature_names
            }, f)
        print(f"✓ Preprocessor saved: {filepath}")
    
    def load_preprocessor(self, filepath='models/preprocessor.pkl'):
        """Load preprocessor objects"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.scaler = data['scaler']
            self.label_encoder = data['label_encoder']
            self.feature_names = data['feature_names']
        print(f"✓ Preprocessor loaded: {filepath}")

if __name__ == "__main__":
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    print("=" * 60)
    print("IDS Data Preprocessing")
    print("=" * 60)
    print("\nNote: Please download NSL-KDD dataset from:")
    print("https://www.unb.ca/cic/datasets/nsl.html")
    print("\nPlace files in 'data/' directory:")
    print("  - KDDTrain+.txt")
    print("  - KDDTest+.txt")
    print("=" * 60)
