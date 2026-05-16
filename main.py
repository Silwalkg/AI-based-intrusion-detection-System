"""
entry point that runs everything in order
"""
"""
Main training pipeline for AI-Powered IDS
Supports combined NSL-KDD + CIC-IDS2017 training.
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
    print("=" * 70)
    print(" " * 15 + "AI-POWERED INTRUSION DETECTION SYSTEM")
    print("=" * 70)

    create_directories()
    log_message("Starting IDS training pipeline")

    # ------------------------------------------------------------------ #
    # STEP 1: Load & combine datasets                                      #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    print("STEP 1: DATA LOADING & PREPROCESSING")
    print("=" * 70)

    preprocessor = DataPreprocessor()

    try:
        train_df, test_df = preprocessor.load_combined(
            nsl_train='data/KDDTrain+.txt',
            nsl_test='data/KDDTest+.txt',
            cic_dir='data/CIC-IDS2017',
        )
    except FileNotFoundError as e:
        print(f"\n✗ {e}")
        print("\nRun:  python download_dataset.py  to get NSL-KDD.")
        return

    # Preprocess
    X_train_full, y_train_full, _ = preprocessor.preprocess_data(train_df, is_training=True)
    X_test,       y_test,       _ = preprocessor.preprocess_data(test_df,  is_training=False)

    # Validation split
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full, test_size=0.2, random_state=42, stratify=y_train_full
    )

    print(f"\n✓ Data split:")
    print(f"  Training:   {X_train.shape[0]:,}")
    print(f"  Validation: {X_val.shape[0]:,}")
    print(f"  Testing:    {X_test.shape[0]:,}")

    preprocessor.save_preprocessor()

    # ------------------------------------------------------------------ #
    # STEP 2: Feature Engineering                                          #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    print("STEP 2: FEATURE ENGINEERING")
    print("=" * 70)

    feature_engineer = FeatureEngineer()
    feature_engineer.calculate_feature_importance(
        X_train, y_train, preprocessor.feature_names, top_k=14
    )
    feature_engineer.plot_feature_importance(top_k=14)

    # ------------------------------------------------------------------ #
    # STEP 3: Model Training                                               #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    print("STEP 3: MODEL TRAINING")
    print("=" * 70)

    trainer = ModelTrainer()

    log_message("Training Random Forest")
    rf_model = trainer.train_random_forest(X_train, y_train)
    trainer.save_model('random_forest')

    log_message("Training XGBoost")
    xgb_model = trainer.train_xgboost(X_train, y_train)
    trainer.save_model('xgboost')

    log_message("Training SVM")
    svm_model = trainer.train_svm(X_train, y_train, sample_size=10000)
    trainer.save_model('svm')

    # Note: Neural Network training skipped (TensorFlow not available on Python 3.14)
    # Using only Random Forest, XGBoost, and SVM models

    # ------------------------------------------------------------------ #
    # STEP 4: Evaluation                                                   #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    print("STEP 4: MODEL EVALUATION")
    print("=" * 70)

    evaluator = ModelEvaluator(label_encoder=preprocessor.label_encoder)

    for name, model in [('Random Forest', rf_model), ('XGBoost', xgb_model),
                        ('SVM', svm_model)]:
        log_message(f"Evaluating {name}")
        evaluator.evaluate_model(model, X_test, y_test, name)

    evaluator.compare_models()
    evaluator.save_results()

    # ------------------------------------------------------------------ #
    # STEP 5: Summary                                                      #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print("\nModels saved to models/")
    print("Results saved to results/")
    print("\nNext: python src/real_time_detection.py")
    log_message("Training pipeline completed successfully")


if __name__ == "__main__":
    main()
