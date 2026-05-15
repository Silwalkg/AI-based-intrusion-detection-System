#!/usr/bin/env python3
"""
Comprehensive system verification for Intrusion Detection System
"""
import os
import sys
import sqlite3
import pickle
import json

print('='*80)
print('SYSTEM VERIFICATION - INTRUSION DETECTION SYSTEM')
print('='*80)

# 1. Check Models
print('\n✓ CHECKING TRAINED MODELS')
print('-'*80)
models_dir = 'models'
required_models = [
    'random_forest.pkl',
    'xgboost.pkl',
    'svm.pkl',
    'neural_network.h5',
    'preprocessor.pkl'
]

models_ok = 0
for model in required_models:
    path = os.path.join(models_dir, model)
    if os.path.exists(path):
        size = os.path.getsize(path) / (1024*1024)
        print(f'  ✅ {model:<30} ({size:.2f} MB)')
        models_ok += 1
    else:
        print(f'  ❌ {model:<30} MISSING')

# 2. Check Datasets
print('\n✓ CHECKING DATASETS')
print('-'*80)
data_dir = 'data'
required_data = [
    'KDDTrain+.txt',
    'KDDTest+.txt'
]

data_ok = 0
for data in required_data:
    path = os.path.join(data_dir, data)
    if os.path.exists(path):
        size = os.path.getsize(path) / (1024*1024)
        print(f'  ✅ {data:<30} ({size:.2f} MB)')
        data_ok += 1
    else:
        print(f'  ❌ {data:<30} MISSING')

# 3. Check Database
print('\n✓ CHECKING DATABASE')
print('-'*80)
db_path = 'detections.db'
db_ok = False
if os.path.exists(db_path):
    size = os.path.getsize(db_path) / (1024*1024)
    print(f'  ✅ detections.db exists ({size:.2f} MB)')
    
    try:
        # Check table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM detections')
        count = cursor.fetchone()[0]
        print(f'  ✅ detections table has {count:,} records')
        
        # Check schema
        cursor.execute('PRAGMA table_info(detections)')
        columns = cursor.fetchall()
        print(f'  ✅ detections table has {len(columns)} columns')
        conn.close()
        db_ok = True
    except Exception as e:
        print(f'  ❌ Database error: {e}')
else:
    print(f'  ⚠️  detections.db not found (will be created on first run)')

# 4. Check Results
print('\n✓ CHECKING TRAINING RESULTS')
print('-'*80)
results_file = 'results/evaluation_results.json'
results_ok = False
if os.path.exists(results_file):
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        print(f'  ✅ evaluation_results.json exists')
        for model, metrics in results.items():
            accuracy = metrics.get('accuracy', 0) * 100
            print(f'     - {model:<20} Accuracy: {accuracy:.2f}%')
        results_ok = True
    except Exception as e:
        print(f'  ❌ Error reading results: {e}')
else:
    print(f'  ❌ evaluation_results.json MISSING')

# 5. Check Source Code
print('\n✓ CHECKING SOURCE CODE')
print('-'*80)
src_files = [
    'src/data_preprocessing.py',
    'src/feature_engineering.py',
    'src/model_training.py',
    'src/model_evaluation.py',
    'src/real_time_detection.py',
    'src/utils.py',
    'app.py',
    'main.py'
]

code_ok = 0
for file in src_files:
    if os.path.exists(file):
        size = os.path.getsize(file) / 1024
        print(f'  ✅ {file:<35} ({size:.1f} KB)')
        code_ok += 1
    else:
        print(f'  ❌ {file:<35} MISSING')

# 6. Check Web UI
print('\n✓ CHECKING WEB UI')
print('-'*80)
ui_files = [
    'templates/index.html',
    'dashboard.html'
]

ui_ok = 0
for file in ui_files:
    if os.path.exists(file):
        size = os.path.getsize(file) / 1024
        print(f'  ✅ {file:<35} ({size:.1f} KB)')
        ui_ok += 1
    else:
        print(f'  ⚠️  {file:<35} (optional)')

# 7. Check Dependencies
print('\n✓ CHECKING PYTHON DEPENDENCIES')
print('-'*80)
dependencies = [
    'numpy',
    'pandas',
    'sklearn',
    'xgboost',
    'tensorflow',
    'flask',
    'scapy',
    'matplotlib',
    'seaborn'
]

deps_ok = 0
for dep in dependencies:
    try:
        __import__(dep)
        print(f'  ✅ {dep:<20} installed')
        deps_ok += 1
    except ImportError:
        if dep == 'tensorflow':
            print(f'  ⚠️  {dep:<20} optional (can use run_without_tensorflow.py)')
            deps_ok += 1
        else:
            print(f'  ❌ {dep:<20} NOT installed')

# 8. Summary
print('\n' + '='*80)
print('SYSTEM STATUS SUMMARY')
print('='*80)

checks = {
    'Models': models_ok == len(required_models),
    'Datasets': data_ok == len(required_data),
    'Database': db_ok,
    'Results': results_ok,
    'Source Code': code_ok == len(src_files),
    'Web UI': ui_ok >= 1,
    'Dependencies': deps_ok >= 8
}

print()
for check, status in checks.items():
    symbol = '✅' if status else '⚠️ '
    status_text = 'OK' if status else 'ISSUE'
    print(f'{symbol} {check:<20} {status_text}')

# Overall status
print('\n' + '='*80)
all_ok = all(checks.values())
if all_ok:
    print('🎉 SYSTEM STATUS: FULLY OPERATIONAL')
    print('='*80)
    print('\nYour Intrusion Detection System is ready to use!')
    print('\nNext steps:')
    print('  1. Run: python app.py')
    print('  2. Open: http://127.0.0.1:8080')
    print('  3. Monitor real-time detections')
else:
    print('⚠️  SYSTEM STATUS: NEEDS ATTENTION')
    print('='*80)
    print('\nSome components need attention. See details above.')

print('\n' + '='*80)
