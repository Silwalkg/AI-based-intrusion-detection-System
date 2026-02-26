"""
Helper script to download NSL-KDD dataset
"""
import os
import urllib.request
import zipfile

def download_nsl_kdd():
    """Download NSL-KDD dataset from GitHub"""
    print("="*60)
    print("NSL-KDD Dataset Downloader")
    print("="*60)
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Dataset URLs
    base_url = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/"
    files = {
        'KDDTrain+.txt': base_url + 'KDDTrain%2B.txt',
        'KDDTest+.txt': base_url + 'KDDTest%2B.txt'
    }
    
    print("\nDownloading NSL-KDD dataset files...")
    
    for filename, url in files.items():
        filepath = os.path.join('data', filename)
        
        if os.path.exists(filepath):
            print(f"✓ {filename} already exists, skipping...")
            continue
        
        try:
            print(f"  Downloading {filename}...")
            urllib.request.urlretrieve(url, filepath)
            print(f"  ✓ {filename} downloaded successfully")
        except Exception as e:
            print(f"  ✗ Error downloading {filename}: {e}")
            print(f"\n  Please download manually from:")
            print(f"  {url}")
            return False
    
    print("\n" + "="*60)
    print("✓ Dataset download complete!")
    print("="*60)
    print("\nFiles downloaded to 'data/' directory:")
    for filename in files.keys():
        filepath = os.path.join('data', filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            print(f"  - {filename} ({size:.2f} MB)")
    
    print("\nYou can now run the training pipeline:")
    print("  python main.py")
    
    return True

if __name__ == "__main__":
    download_nsl_kdd()
