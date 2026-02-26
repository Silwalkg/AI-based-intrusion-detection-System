"""
Main training pipeline for AI-Powered IDS
"""
import sys
import os
sys.path.append('src')

import numpy as np
from sklearn.model_selection import train_test_split
from data_preprocessing import DataPreprocessor
from feature_engineering import FeatureEngineer
from model_training import ModelTrainer
from model_evaluation import ModelEvaluator
from utils import create_directories, log_message
import warnings
warnings.filterwarnings('ignore')

def main():
    print("="*70)
    print(" "*15 + "AI-POWERED INTRUSION DETECTION SYSTEM")
    print("="*70)
    
    # Create directories
    create_directories()
    log_message("Starting IDS training pipeline")
    
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
        print("\nAlternatively, you can download from:")
        print("https://github.com/defcom17/NSL_KDD")
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
    print("STEP 3: MODEL TRAINING")
    print("="*70)
    
    trainer = ModelTrainer()
    
    # Train Random Forest
    log_message("Training Random Forest")
    rf_model = trainer.train_random_forest(X_train, y_train, hyperparameter_tuning=False)
    trainer.save_model('random_forest')
    
    # Train XGBoost
    log_message("Training XGBoost")
    xgb_model = trainer.train_xgboost(X_train, y_train, hyperparameter_tuning=False)
    trainer.save_model('xgboost')
    
    # Train SVM (on subset)
    log_message("Training SVM")
    svm_model = trainer.train_svm(X_train, y_train, sample_size=10000)
    trainer.save_model('svm')
    
    # Train Neural Network
    log_message("Training Neural Network")
    num_classes = len(np.unique(y_train))
    nn_model, history = trainer.train_neural_network(X_train, y_train, X_val, y_val, num_classes)
    trainer.save_model('neural_network')
    
    # Step 4: Model Evaluation
    print("\n" + "="*70)
    print("STEP 4: MODEL EVALUATION")
    print("="*70)
    
    evaluator = ModelEvaluator(label_encoder=preprocessor.label_encoder)
    
    # Evaluate all models
    log_message("Evaluating Random Forest")
    evaluator.evaluate_model(rf_model, X_test, y_test, 'Random Forest')
    
    log_message("Evaluating XGBoost")
    evaluator.evaluate_model(xgb_model, X_test, y_test, 'XGBoost')
    
    log_message("Evaluating SVM")
    evaluator.evaluate_model(svm_model, X_test, y_test, 'SVM')
    
    log_message("Evaluating Neural Network")
    evaluator.evaluate_model(nn_model, X_test, y_test, 'Neural Network')
    
    # Compare models
    comparison_df = evaluator.compare_models()
    
    # Save results
    evaluator.save_results()
    
    # Step 5: Summary
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    
    print("\n📁 Generated Files:")
    print("  Models:")
    print("    - models/random_forest.pkl")
    print("    - models/xgboost.pkl")
    print("    - models/svm.pkl")
    print("    - models/neural_network.h5")
    print("    - models/preprocessor.pkl")
    print("\n  Results:")
    print("    - results/evaluation_results.json")
    print("    - results/model_comparison.png")
    print("    - results/feature_importance.png")
    print("    - results/confusion_matrix_*.png")
    print("    - results/training.log")
    
    print("\n🚀 Next Steps:")
    print("  1. Review evaluation results in 'results/' directory")
    print("  2. Test real-time detection:")
    print("     python src/real_time_detection.py")
    print("  3. Integrate best model into production system")
    
    log_message("Training pipeline completed successfully")

if __name__ == "__main__":
    main()
