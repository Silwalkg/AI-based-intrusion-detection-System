"""
Quick system test to verify installation and basic functionality
"""
import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("="*60)
    print("Testing Package Imports")
    print("="*60)
    
    packages = [
        ('numpy', 'np'),
        ('pandas', 'pd'),
        ('sklearn', 'sklearn'),
        ('xgboost', 'xgb'),
        ('tensorflow', 'tf'),
        ('matplotlib.pyplot', 'plt'),
        ('seaborn', 'sns')
    ]
    
    failed = []
    for package, alias in packages:
        try:
            __import__(package)
            print(f"✓ {package:20s} - OK")
        except ImportError:
            print(f"✗ {package:20s} - MISSING")
            failed.append(package)
    
    if failed:
        print(f"\n⚠ Missing packages: {', '.join(failed)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All packages installed successfully")
        return True

def test_directory_structure():
    """Test if directory structure is correct"""
    print("\n" + "="*60)
    print("Testing Directory Structure")
    print("="*60)
    
    required_dirs = ['data', 'models', 'results', 'notebooks', 'src']
    required_files = [
        'src/data_preprocessing.py',
        'src/feature_engineering.py',
        'src/model_training.py',
        'src/model_evaluation.py',
        'src/real_time_detection.py',
        'src/utils.py',
        'main.py',
        'requirements.txt'
    ]
    
    # Check directories
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ Directory: {dir_name}")
        else:
            print(f"✗ Directory missing: {dir_name}")
            os.makedirs(dir_name, exist_ok=True)
            print(f"  Created: {dir_name}")
    
    # Check files
    print()
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ File: {file_path}")
        else:
            print(f"✗ File missing: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠ Missing files: {len(missing_files)}")
        return False
    else:
        print("\n✓ All required files present")
        return True

def test_dataset():
    """Test if dataset is available"""
    print("\n" + "="*60)
    print("Testing Dataset Availability")
    print("="*60)
    
    dataset_files = ['data/KDDTrain+.txt', 'data/KDDTest+.txt']
    
    all_present = True
    for file_path in dataset_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"✓ {file_path} ({size:.2f} MB)")
        else:
            print(f"✗ {file_path} - NOT FOUND")
            all_present = False
    
    if not all_present:
        print("\n⚠ Dataset not found!")
        print("\nDownload options:")
        print("  1. Run: python download_dataset.py")
        print("  2. Manual download from: https://www.unb.ca/cic/datasets/nsl.html")
        print("  3. GitHub: https://github.com/defcom17/NSL_KDD")
        return False
    else:
        print("\n✓ Dataset files present")
        return True

def test_module_imports():
    """Test if custom modules can be imported"""
    print("\n" + "="*60)
    print("Testing Custom Module Imports")
    print("="*60)
    
    sys.path.append('src')
    
    modules = [
        'utils',
        'data_preprocessing',
        'feature_engineering',
        'model_training',
        'model_evaluation',
        'real_time_detection'
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module} - Error: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠ Failed to import: {', '.join(failed)}")
        return False
    else:
        print("\n✓ All custom modules imported successfully")
        return True

def run_all_tests():
    """Run all system tests"""
    print("\n" + "="*70)
    print(" "*20 + "IDS SYSTEM TEST")
    print("="*70)
    
    results = {
        'Package Imports': test_imports(),
        'Directory Structure': test_directory_structure(),
        'Dataset Availability': test_dataset(),
        'Module Imports': test_module_imports()
    }
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:25s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("="*70)
        print("\nSystem is ready! You can now:")
        print("  1. Run exploratory analysis: python notebooks/exploratory_analysis.py")
        print("  2. Train models: python main.py")
        print("  3. Test real-time detection: python src/real_time_detection.py")
    else:
        print("⚠ SOME TESTS FAILED")
        print("="*70)
        print("\nPlease fix the issues above before proceeding.")
        print("Refer to SETUP_GUIDE.md for detailed instructions.")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
