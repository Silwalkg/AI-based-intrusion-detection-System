"""
Main training pipeline for AI-Powered IDS (Without TensorFlow)
"""
import sys
import os
sys.path.append('src')

import numpy as np
from sklearn.model_selection import train_test_split
from data_preprocessing import DataPreprocessor
from feature_engineering import FeatureEngineer
from utils import create_directories, log_message
import warnings
warnings.filterwarnings('ignore')

# Import only non-TensorFlow models
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
import pickle
import time

def main():
    print("="*70)
    print(" "*15 + "AI-POWERED INTRUSION DETECTION SYSTEM")
    print(" "*20 + "(Without Neural Network)")
    print("="*70)
    
    # Create directories
    create_directories()
    log_message("Starting IDS training pipeline (without TensorFlow)")
    
    # Step 1: Data Preprocessing
    print("\n" + "="*70)
    print("STEP 1: DATA PREPROCESSING")
    print("="*70)
    
    preprocessor = DataPreprocessor(dataset_type='nsl-kdd')
    
    try:
        # Load NSL-KDD dataset
        train_df, test_df = preprocessor.load_nsl_kdd(
            train_path='data/KDDTrain+.txt',
            test_path='data/KDDTest+.txt'
        )
        
        # Preprocess training data
        X_train_full, y_train_full, y_train_labels = preprocessor.preprocess_data(train_df, is_training=True)
        
        # Preprocess test data
        X_test, y_test, y_test_labels = preprocessor.preprocess_data(test_df, is_training=False)
        
        # Split training data for validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_full, y_train_full, test_size=0.2, random_state=42, stratify=y_train_full
        )
        
        print(f"\n✓ Data split:")
        print(f"  Training:   {X_train.shape[0]} samples")
        print(f"  Validation: {X_val.shape[0]} samples")
        print(f"  Testing:    {X_test.shape[0]} samples")
        
        # Save preprocessor
        preprocessor.save_preprocessor()
        
    except FileNotFoundError:
        print("\n⚠ NSL-KDD dataset not found!")
        print("\nPlease download the dataset from:")
        print("https://www.unb.ca/cic/datasets/nsl.html")
        print("\nPlace these files in the 'data/' directory:")
        print("  - KDDTrain+.txt")
        print("  - KDDTest+.txt")
        return
    
    # Step 2: Feature Engineering
    print("\n" + "="*70)
    print("STEP 2: FEATURE ENGINEERING")
    print("="*70)
    
    feature_engineer = FeatureEngineer()
    
    # Calculate feature importance
    importance_df = feature_engineer.calculate_feature_importance(
        X_train, y_train, preprocessor.feature_names, top_k=20
    )
    
    # Plot feature importance
    feature_engineer.plot_feature_importance(top_k=20)
    
    # Step 3: Model Training
    print("\n" + "="*70)
    print("STEP 3: MODEL TRAINING (3 Models)")
    print("="*70)
    
    models = {}
    
    # Train Random Forest
    print("\n" + "-"*60)
    print("Training Random Forest...")
    print("-"*60)
    log_message("Training Random Forest")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1
    )
    start_time = time.time()
    rf.fit(X_train, y_train)
    training_time = time.time() - start_time
    models['random_forest'] = rf
    print(f"✓ Training completed in {training_time:.2f} seconds")
    
    # Save model
    with open('models/random_forest.pkl', 'wb') as f:
        pickle.dump(rf, f)
    print("✓ Model saved: models/random_forest.pkl")
    
    # Train XGBoost
    print("\n" + "-"*60)
    print("Training XGBoost...")
    print("-"*60)
    log_message("Training XGBoost")
    xgb = XGBClassifier(
        n_estimators=200,
        max_depth=10,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
        n_jobs=-1,
        eval_metric='mlogloss'
    )
    start_time = time.time()
    xgb.fit(X_train, y_train)
    training_time = time.time() - start_time
    models['xgboost'] = xgb
    print(f"✓ Training completed in {training_time:.2f} seconds")
    
    # Save model
    with open('models/xgboost.pkl', 'wb') as f:
        pickle.dump(xgb, f)
    print("✓ Model saved: models/xgboost.pkl")
    
    # Train SVM (on subset)
    print("\n" + "-"*60)
    print("Training SVM...")
    print("-"*60)
    log_message("Training SVM")
    sample_size = 10000
    print(f"⚠ Using {sample_size} samples for SVM training (computational efficiency)")
    indices = np.random.choice(len(X_train), sample_size, replace=False)
    X_train_subset = X_train[indices]
    y_train_subset = y_train[indices]
    
    svm = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
    start_time = time.time()
    svm.fit(X_train_subset, y_train_subset)
    training_time = time.time() - start_time
    models['svm'] = svm
    print(f"✓ Training completed in {training_time:.2f} seconds")
    
    # Save model
    with open('models/svm.pkl', 'wb') as f:
        pickle.dump(svm, f)
    print("✓ Model saved: models/svm.pkl")
    
    # Step 4: Model Evaluation
    print("\n" + "="*70)
    print("STEP 4: MODEL EVALUATION")
    print("="*70)
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    results = {}
    
    for model_name, model in models.items():
        print(f"\n{'-'*60}")
        print(f"Evaluating {model_name.replace('_', ' ').title()}")
        print('-'*60)
        
        # Predict
        start_time = time.time()
        y_pred = model.predict(X_test)
        prediction_time = time.time() - start_time
        avg_latency = (prediction_time / len(X_test)) * 1000  # ms
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        results[model_name] = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'avg_latency_ms': float(avg_latency)
        }
        
        print(f"\n📊 Performance Metrics:")
        print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
        print(f"\n⚡ Latency:")
        print(f"  Average:   {avg_latency:.4f} ms/sample")
        print(f"  Total:     {prediction_time:.4f} seconds")
    
    # Step 5: Model Comparison
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)
    
    import pandas as pd
    df = pd.DataFrame(results).T
    print("\n", df.to_string())
    
    # Find best model
    best_model = df['accuracy'].idxmax()
    best_accuracy = df.loc[best_model, 'accuracy']
    best_latency = df.loc[best_model, 'avg_latency_ms']
    
    print(f"\n🏆 Best Model: {best_model.replace('_', ' ').title()}")
    print(f"   Accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
    print(f"   Latency:  {best_latency:.4f} ms")
    
    # Check requirements
    if best_accuracy >= 0.95 and best_latency < 50:
        print("\n✅ System meets all requirements!")
        print(f"   ✓ Accuracy ≥ 95%: {best_accuracy*100:.2f}%")
        print(f"   ✓ Latency < 50ms: {best_latency:.4f} ms")
    else:
        print("\n⚠ System requirements check:")
        if best_accuracy >= 0.95:
            print(f"   ✓ Accuracy ≥ 95%: {best_accuracy*100:.2f}%")
        else:
            print(f"   ✗ Accuracy < 95%: {best_accuracy*100:.2f}%")
        if best_latency < 50:
            print(f"   ✓ Latency < 50ms: {best_latency:.4f} ms")
        else:
            print(f"   ✗ Latency ≥ 50ms: {best_latency:.4f} ms")
    
    # Save results
    import json
    os.makedirs('results', exist_ok=True)
    with open('results/evaluation_results_no_tf.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("\n✓ Results saved: results/evaluation_results_no_tf.json")
    
    # Step 6: Summary
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    
    print("\n📁 Generated Files:")
    print("  Models:")
    print("    - models/random_forest.pkl")
    print("    - models/xgboost.pkl")
    print("    - models/svm.pkl")
    print("    - models/preprocessor.pkl")
    print("\n  Results:")
    print("    - results/evaluation_results_no_tf.json")
    print("    - results/feature_importance.png")
    print("    - results/training.log")
    
    print("\n🚀 Next Steps:")
    print("  1. Review evaluation results")
    print("  2. Test real-time detection:")
    print("     python src/real_time_detection.py")
    print("  3. Integrate best model into production system")
    
    print("\n💡 Note: Neural Network training skipped (TensorFlow not available)")
    print("   Install TensorFlow with Python 3.8-3.11 to train Neural Network")
    
    log_message("Training pipeline completed successfully (without TensorFlow)")

if __name__ == "__main__":
    main()
