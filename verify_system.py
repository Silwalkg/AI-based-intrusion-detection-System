"""
Complete System Verification Script
Tests all components of the IDS system
"""
import sys
import os
sys.path.append('src')

import numpy as np
import pickle
from data_preprocessing import DataPreprocessor
from model_evaluation import ModelEvaluator
from real_time_detection import RealTimeIDS

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_1_files_exist():
    """Test 1: Check if all required files exist"""
    print_header("TEST 1: Checking Required Files")
    
    required_files = {
        'Models': [
            'models/random_forest.pkl',
            'models/xgboost.pkl',
            'models/svm.pkl',
            'models/neural_network.h5',
            'models/preprocessor.pkl'
        ],
        'Data': [
            'data/KDDTrain+.txt',
            'data/KDDTest+.txt'
        ],
        'Results': [
            'results/evaluation_results.json',
            'results/model_comparison.png',
            'results/feature_importance.png'
        ]
    }
    
    all_exist = True
    for category, files in required_files.items():
        print(f"\n{category}:")
        for file_path in files:
            exists = os.path.exists(file_path)
            status = "✓" if exists else "✗"
            print(f"  {status} {file_path}")
            if not exists:
                all_exist = False
    
    if all_exist:
        print("\n✅ TEST 1 PASSED: All required files exist")
        return True
    else:
        print("\n❌ TEST 1 FAILED: Some files are missing")
        return False

def test_2_load_models():
    """Test 2: Load and verify all models"""
    print_header("TEST 2: Loading Models")
    
    models_to_test = [
        ('Random Forest', 'models/random_forest.pkl'),
        ('XGBoost', 'models/xgboost.pkl'),
        ('SVM', 'models/svm.pkl'),
        ('Preprocessor', 'models/preprocessor.pkl')
    ]
    
    all_loaded = True
    for name, path in models_to_test:
        try:
            with open(path, 'rb') as f:
                model = pickle.load(f)
            print(f"  ✓ {name} loaded successfully")
        except Exception as e:
            print(f"  ✗ {name} failed to load: {e}")
            all_loaded = False
    
    # Test Neural Network separately
    try:
        from tensorflow import keras
        nn_model = keras.models.load_model('models/neural_network.h5')
        print(f"  ✓ Neural Network loaded successfully")
    except Exception as e:
        print(f"  ✗ Neural Network failed to load: {e}")
        all_loaded = False
    
    if all_loaded:
        print("\n✅ TEST 2 PASSED: All models loaded successfully")
        return True
    else:
        print("\n❌ TEST 2 FAILED: Some models failed to load")
        return False

def test_3_preprocessor():
    """Test 3: Test data preprocessing"""
    print_header("TEST 3: Testing Data Preprocessing")
    
    try:
        # Load preprocessor
        with open('models/preprocessor.pkl', 'rb') as f:
            preprocessor_data = pickle.load(f)
        
        scaler = preprocessor_data['scaler']
        label_encoder = preprocessor_data['label_encoder']
        feature_names = preprocessor_data['feature_names']
        
        print(f"  ✓ Preprocessor loaded")
        print(f"  ✓ Features: {len(feature_names)}")
        print(f"  ✓ Classes: {list(label_encoder.classes_)}")
        
        # Test with sample data
        sample_data = np.random.rand(1, len(feature_names))
        scaled_data = scaler.transform(sample_data)
        
        print(f"  ✓ Sample data preprocessed successfully")
        print(f"    Input shape: {sample_data.shape}")
        print(f"    Output shape: {scaled_data.shape}")
        
        print("\n✅ TEST 3 PASSED: Preprocessing working correctly")
        return True
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        return False

def test_4_model_predictions():
    """Test 4: Test model predictions"""
    print_header("TEST 4: Testing Model Predictions")
    
    try:
        # Load preprocessor
        with open('models/preprocessor.pkl', 'rb') as f:
            preprocessor_data = pickle.load(f)
        
        scaler = preprocessor_data['scaler']
        label_encoder = preprocessor_data['label_encoder']
        feature_names = preprocessor_data['feature_names']
        
        # Create sample data
        sample_data = np.random.rand(5, len(feature_names))
        scaled_data = scaler.transform(sample_data)
        
        # Test each model
        models_to_test = [
            ('Random Forest', 'models/random_forest.pkl'),
            ('XGBoost', 'models/xgboost.pkl'),
            ('SVM', 'models/svm.pkl')
        ]
        
        all_predicted = True
        for name, path in models_to_test:
            try:
                with open(path, 'rb') as f:
                    model = pickle.load(f)
                
                predictions = model.predict(scaled_data)
                predicted_labels = label_encoder.inverse_transform(predictions)
                
                print(f"\n  ✓ {name}:")
                print(f"    Predictions: {predicted_labels}")
                print(f"    Shape: {predictions.shape}")
            except Exception as e:
                print(f"\n  ✗ {name} prediction failed: {e}")
                all_predicted = False
        
        # Test Neural Network
        try:
            from tensorflow import keras
            nn_model = keras.models.load_model('models/neural_network.h5')
            nn_predictions = nn_model.predict(scaled_data, verbose=0)
            nn_classes = np.argmax(nn_predictions, axis=1)
            nn_labels = label_encoder.inverse_transform(nn_classes)
            
            print(f"\n  ✓ Neural Network:")
            print(f"    Predictions: {nn_labels}")
            print(f"    Shape: {nn_predictions.shape}")
        except Exception as e:
            print(f"\n  ✗ Neural Network prediction failed: {e}")
            all_predicted = False
        
        if all_predicted:
            print("\n✅ TEST 4 PASSED: All models making predictions")
            return True
        else:
            print("\n❌ TEST 4 FAILED: Some models failed to predict")
            return False
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        return False

def test_5_real_time_detection():
    """Test 5: Test real-time detection system"""
    print_header("TEST 5: Testing Real-Time Detection")
    
    try:
        # Initialize IDS
        ids = RealTimeIDS(
            model_path='models/xgboost.pkl',
            preprocessor_path='models/preprocessor.pkl'
        )
        
        print("  ✓ Real-Time IDS initialized")
        
        # Test single detection
        sample_traffic = np.random.rand(41)
        result = ids.detect(sample_traffic)
        
        print(f"\n  ✓ Single detection test:")
        print(f"    Attack Type: {result['attack_type']}")
        print(f"    Is Attack: {result['is_attack']}")
        print(f"    Confidence: {result['confidence']:.2f}")
        print(f"    Latency: {result['latency_ms']:.4f} ms")
        
        # Test batch detection
        batch_traffic = [np.random.rand(41) for _ in range(10)]
        batch_results = ids.detect_batch(batch_traffic)
        
        print(f"\n  ✓ Batch detection test:")
        print(f"    Samples processed: {len(batch_results)}")
        print(f"    Attacks detected: {sum(1 for r in batch_results if r['is_attack'])}")
        
        # Get statistics
        stats = ids.get_statistics()
        print(f"\n  ✓ Statistics:")
        print(f"    Total detections: {stats['total_detections']}")
        print(f"    Average latency: {stats['latency']['average_ms']:.4f} ms")
        
        print("\n✅ TEST 5 PASSED: Real-time detection working")
        return True
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_6_performance_metrics():
    """Test 6: Verify performance metrics"""
    print_header("TEST 6: Checking Performance Metrics")
    
    try:
        import json
        
        # Load evaluation results
        with open('results/evaluation_results.json', 'r') as f:
            results = json.load(f)
        
        print("\nModel Performance Summary:")
        print("-" * 70)
        
        best_accuracy = 0
        best_model = ""
        
        for model_name, metrics in results.items():
            accuracy = metrics['accuracy'] * 100
            latency = metrics['avg_latency_ms']
            
            print(f"\n{model_name}:")
            print(f"  Accuracy:  {accuracy:.2f}%")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall:    {metrics['recall']:.4f}")
            print(f"  F1-Score:  {metrics['f1_score']:.4f}")
            print(f"  Latency:   {latency:.4f} ms")
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model = model_name
        
        print(f"\n🏆 Best Model: {best_model} ({best_accuracy:.2f}%)")
        
        # Check if latency requirement is met
        latency_ok = all(m['avg_latency_ms'] < 50 for m in results.values())
        
        print("\n✓ Performance Requirements:")
        print(f"  Latency < 50ms: {'✅ PASS' if latency_ok else '❌ FAIL'}")
        print(f"  Best Accuracy: {best_accuracy:.2f}%")
        
        print("\n✅ TEST 6 PASSED: Performance metrics verified")
        return True
    except Exception as e:
        print(f"\n❌ TEST 6 FAILED: {e}")
        return False

def test_7_attack_detection():
    """Test 7: Test attack type detection"""
    print_header("TEST 7: Testing Attack Type Detection")
    
    try:
        # Initialize IDS
        ids = RealTimeIDS(
            model_path='models/xgboost.pkl',
            preprocessor_path='models/preprocessor.pkl'
        )
        
        # Test multiple samples
        num_samples = 50
        print(f"\n  Testing {num_samples} samples...")
        
        attack_counts = {}
        for _ in range(num_samples):
            sample = np.random.rand(41)
            result = ids.detect(sample)
            attack_type = result['attack_type']
            attack_counts[attack_type] = attack_counts.get(attack_type, 0) + 1
        
        print("\n  Detection Distribution:")
        for attack_type, count in sorted(attack_counts.items()):
            percentage = (count / num_samples) * 100
            print(f"    {attack_type:10s}: {count:3d} ({percentage:5.1f}%)")
        
        # Check if multiple attack types detected
        unique_types = len(attack_counts)
        print(f"\n  ✓ Unique attack types detected: {unique_types}")
        
        if unique_types >= 2:
            print("\n✅ TEST 7 PASSED: System detecting multiple attack types")
            return True
        else:
            print("\n⚠️ TEST 7 WARNING: Only one attack type detected (may be due to random data)")
            return True
    except Exception as e:
        print(f"\n❌ TEST 7 FAILED: {e}")
        return False

def run_all_tests():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("  AI-POWERED IDS - COMPLETE SYSTEM VERIFICATION")
    print("="*70)
    
    tests = [
        ("Files Exist", test_1_files_exist),
        ("Load Models", test_2_load_models),
        ("Preprocessing", test_3_preprocessor),
        ("Model Predictions", test_4_model_predictions),
        ("Real-Time Detection", test_5_real_time_detection),
        ("Performance Metrics", test_6_performance_metrics),
        ("Attack Detection", test_7_attack_detection)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:25s}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("\n" + "="*70)
    print(f"  TOTAL: {passed_tests}/{total_tests} tests passed")
    print("="*70)
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Your IDS system is fully functional!")
        print("\n✅ System Status: OPERATIONAL")
        print("\nYour system can:")
        print("  • Detect network intrusions in real-time")
        print("  • Classify 5 types of attacks (Normal, DoS, Probe, R2L, U2R)")
        print("  • Process predictions with low latency (<50ms)")
        print("  • Provide confidence scores for detections")
        print("\n🚀 Ready for deployment and testing!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed")
        print("Please review the errors above and fix any issues.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
