"""
Exploratory Data Analysis for IDS
Run this notebook to understand the dataset characteristics
"""
import sys
sys.path.append('../src')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data_preprocessing import DataPreprocessor

def analyze_dataset():
    """Perform exploratory data analysis"""
    print("="*60)
    print("EXPLORATORY DATA ANALYSIS - NSL-KDD Dataset")
    print("="*60)
    
    preprocessor = DataPreprocessor()
    
    try:
        train_df, test_df = preprocessor.load_nsl_kdd(
            train_path='../data/KDDTrain+.txt',
            test_path='../data/KDDTest+.txt'
        )
    except FileNotFoundError:
        print("\n⚠ Dataset not found. Please download NSL-KDD dataset first.")
        return
    
    # Add attack categories
    train_df['attack_category'] = train_df['label'].apply(preprocessor.categorize_attacks)
    test_df['attack_category'] = test_df['label'].apply(preprocessor.categorize_attacks)
    
    # 1. Dataset Overview
    print("\n1. DATASET OVERVIEW")
    print("-" * 60)
    print(f"Training samples: {len(train_df)}")
    print(f"Testing samples:  {len(test_df)}")
    print(f"Total features:   {len(train_df.columns) - 2}")  # Exclude label and attack_category
    
    # 2. Attack Distribution
    print("\n2. ATTACK DISTRIBUTION")
    print("-" * 60)
    print("\nTraining Set:")
    print(train_df['attack_category'].value_counts())
    print("\nTesting Set:")
    print(test_df['attack_category'].value_counts())
    
    # 3. Class Imbalance
    print("\n3. CLASS IMBALANCE ANALYSIS")
    print("-" * 60)
    train_dist = train_df['attack_category'].value_counts(normalize=True) * 100
    print("\nTraining Set Percentages:")
    for category, percentage in train_dist.items():
        print(f"  {category:10s}: {percentage:6.2f}%")
    
    # 4. Visualizations
    print("\n4. GENERATING VISUALIZATIONS")
    print("-" * 60)
    
    # Attack distribution plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    train_df['attack_category'].value_counts().plot(kind='bar', ax=axes[0], color='skyblue', edgecolor='black')
    axes[0].set_title('Training Set - Attack Distribution', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Attack Category')
    axes[0].set_ylabel('Count')
    axes[0].tick_params(axis='x', rotation=45)
    
    test_df['attack_category'].value_counts().plot(kind='bar', ax=axes[1], color='lightcoral', edgecolor='black')
    axes[1].set_title('Testing Set - Attack Distribution', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Attack Category')
    axes[1].set_ylabel('Count')
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('../results/attack_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Attack distribution plot saved: results/attack_distribution.png")
    plt.close()
    
    # Feature statistics
    print("\n5. FEATURE STATISTICS")
    print("-" * 60)
    numeric_cols = train_df.select_dtypes(include=[np.number]).columns
    print(f"\nNumeric features: {len(numeric_cols)}")
    print("\nSample statistics (first 5 numeric features):")
    print(train_df[numeric_cols[:5]].describe())
    
    # Correlation analysis
    print("\n6. CORRELATION ANALYSIS")
    print("-" * 60)
    print("Computing correlation matrix for top features...")
    
    # Select top numeric features
    top_features = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count']
    if all(feat in train_df.columns for feat in top_features):
        corr_matrix = train_df[top_features].corr()
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                    square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Feature Correlation Matrix', fontsize=12, fontweight='bold')
        plt.tight_layout()
        plt.savefig('../results/correlation_matrix.png', dpi=300, bbox_inches='tight')
        print("✓ Correlation matrix saved: results/correlation_matrix.png")
        plt.close()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nGenerated visualizations:")
    print("  - results/attack_distribution.png")
    print("  - results/correlation_matrix.png")

if __name__ == "__main__":
    analyze_dataset()
