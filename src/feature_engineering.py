"""
Feature engineering and selection module
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, mutual_info_classif, chi2
import matplotlib.pyplot as plt
import seaborn as sns

class FeatureEngineer:
    def __init__(self):
        self.selected_features = None
        self.feature_importance = None
    
    def calculate_feature_importance(self, X, y, feature_names, top_k=20):
        """Calculate feature importance using Random Forest"""
        print("Calculating feature importance...")
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self.feature_importance = importance_df
        print(f"✓ Top {top_k} important features identified")
        print("\nTop 10 Features:")
        print(importance_df.head(10).to_string(index=False))
        
        return importance_df
    
    def select_features(self, X, y, method='mutual_info', k=30):
        """Select top k features"""
        print(f"\nSelecting top {k} features using {method}...")
        
        if method == 'mutual_info':
            selector = SelectKBest(mutual_info_classif, k=k)
        elif method == 'chi2':
            # Ensure non-negative values for chi2
            X_positive = X - X.min() + 1e-10
            selector = SelectKBest(chi2, k=k)
            X = X_positive
        else:
            raise ValueError(f"Unknown method: {method}")
        
        X_selected = selector.fit_transform(X, y)
        self.selected_features = selector.get_support(indices=True)
        
        print(f"✓ Selected {k} features from {X.shape[1]} total features")
        return X_selected, self.selected_features
    
    def create_statistical_features(self, df):
        """Create additional statistical features"""
        print("Creating statistical features...")
        
        # Rate-based features
        if 'count' in df.columns and 'srv_count' in df.columns:
            df['srv_count_ratio'] = df['srv_count'] / (df['count'] + 1)
        
        # Byte-based features
        if 'src_bytes' in df.columns and 'dst_bytes' in df.columns:
            df['byte_ratio'] = df['src_bytes'] / (df['dst_bytes'] + 1)
            df['total_bytes'] = df['src_bytes'] + df['dst_bytes']
        
        print("✓ Statistical features created")
        return df
    
    def plot_feature_importance(self, top_k=20, save_path='results/feature_importance.png'):
        """Plot feature importance"""
        if self.feature_importance is None:
            print("⚠ No feature importance calculated yet")
            return
        
        plt.figure(figsize=(10, 8))
        top_features = self.feature_importance.head(top_k)
        
        sns.barplot(data=top_features, x='importance', y='feature', palette='viridis')
        plt.title(f'Top {top_k} Feature Importance', fontsize=14, fontweight='bold')
        plt.xlabel('Importance Score', fontsize=12)
        plt.ylabel('Features', fontsize=12)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Feature importance plot saved: {save_path}")
        plt.close()

if __name__ == "__main__":
    print("Feature Engineering Module")
    print("This module is used by the training pipeline")
