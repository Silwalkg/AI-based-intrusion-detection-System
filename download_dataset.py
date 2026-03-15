"""
Dataset downloader for IDS project.
- NSL-KDD: downloaded from GitHub automatically
- CIC-IDS2017: downloaded via nids-datasets package (pip install nids-datasets)
"""
import os
import urllib.request


def download_nsl_kdd():
    """Download NSL-KDD dataset from GitHub."""
    print("=" * 60)
    print("NSL-KDD Dataset Downloader")
    print("=" * 60)

    os.makedirs('data', exist_ok=True)

    base_url = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/"
    files = {
        'KDDTrain+.txt': base_url + 'KDDTrain%2B.txt',
        'KDDTest+.txt':  base_url + 'KDDTest%2B.txt',
    }

    print("\nDownloading NSL-KDD files...")
    for filename, url in files.items():
        filepath = os.path.join('data', filename)
        if os.path.exists(filepath):
            print(f"  ✓ {filename} already exists, skipping.")
            continue
        try:
            print(f"  Downloading {filename}...")
            urllib.request.urlretrieve(url, filepath)
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  ✓ {filename} ({size_mb:.2f} MB)")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            return False

    print("✓ NSL-KDD ready.\n")
    return True


def download_cic_ids2017():
    """Download CIC-IDS2017 Network-Flows subset via nids-datasets package."""
    print("=" * 60)
    print("CIC-IDS2017 Dataset Downloader")
    print("=" * 60)

    # Check if already downloaded (nids-datasets saves as CICIDS_Flow.parquet)
    out_path = os.path.join('data', 'CIC-IDS2017', 'Network-Flows', 'CICIDS_Flow.parquet')
    if os.path.exists(out_path):
        print(f"  ✓ CIC-IDS2017 already downloaded at {out_path}")
        return True

    # Install nids-datasets if needed
    try:
        from nids_datasets import Dataset
    except ImportError:
        print("  Installing nids-datasets package...")
        import subprocess, sys
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'nids-datasets'])
        from nids_datasets import Dataset

    os.makedirs('data/CIC-IDS2017', exist_ok=True)

    print("  Downloading CIC-IDS2017 Network-Flows (this may take a few minutes)...")
    print("  Note: ~500MB download\n")

    try:
        # Change working dir temporarily so files land in data/CIC-IDS2017
        original_dir = os.getcwd()
        os.chdir('data/CIC-IDS2017')

        data = Dataset(dataset='CIC-IDS2017', subset=['Network-Flows'], files='all')
        data.download()

        os.chdir(original_dir)
        print("\n  ✓ CIC-IDS2017 downloaded successfully.")
        return True

    except Exception as e:
        try:
            os.chdir(original_dir)
        except Exception:
            pass
        print(f"\n  ✗ Download failed: {e}")
        print("\n  Fallback: download manually from Kaggle:")
        print("  https://www.kaggle.com/datasets/cicdataset/cicids2017")
        print("  Place CSV files in: data/CIC-IDS2017/")
        return False


def check_status():
    """Print current dataset availability."""
    print("\n" + "=" * 60)
    print("Dataset Status")
    print("=" * 60)

    nsl_train = os.path.exists('data/KDDTrain+.txt')
    nsl_test  = os.path.exists('data/KDDTest+.txt')

    cic_parquet = os.path.exists('data/CIC-IDS2017/CIC_Flow.parquet')
    cic_csv     = os.path.isdir('data/CIC-IDS2017') and any(
        f.endswith('.csv') for f in os.listdir('data/CIC-IDS2017')
    ) if os.path.isdir('data/CIC-IDS2017') else False

    print(f"  NSL-KDD Train  : {'✓' if nsl_train else '✗'}")
    print(f"  NSL-KDD Test   : {'✓' if nsl_test  else '✗'}")
    print(f"  CIC-IDS2017    : {'✓ (parquet)' if cic_parquet else ('✓ (csv)' if cic_csv else '✗')}")

    if nsl_train and nsl_test and (cic_parquet or cic_csv):
        print("\n  ✅ Both datasets ready — combined training will run.")
    elif nsl_train and nsl_test:
        print("\n  ⚠  NSL-KDD only. Run this script to also get CIC-IDS2017.")
    else:
        print("\n  ✗  Missing datasets. Run this script to download.")


if __name__ == "__main__":
    download_nsl_kdd()
    download_cic_ids2017()
    check_status()
