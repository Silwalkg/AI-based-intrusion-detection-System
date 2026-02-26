"""
Model evaluation and performance metrics
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)
from sklearn.preprocessing import label_binarize
import time
import json
import os

class ModelEvaluator:
    def __init__(self, label_encoder=None):
        self.label_encoder = label_encoder
        self.results = {}
    
    def evaluate_model(self, model, X_test, y_test, model_name):
        """Comprehensive model evaluation"""
        print(f"\n{'='*60}")
        print(f"Evaluating {model_name}")
        print('='*60)
        
        # Prediction time (latency)
        start_time = time.time()
        y_pred = model.predict(X_test)
        
        # Handle Neural Network predictions (probabilities to class labels)
        if len(y_pred.shape) > 1 and y_pred.shape[1] > 1:
            y_pred = np.argmax(y_pred, axis=1)
        
        prediction_time = time.time() - start_time
        avg_latency = (prediction_time / len(X_test)) * 1000  # ms per sample
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Store results
        self.results[model_name] = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'avg_latency_ms': float(avg_latency),
            'total_prediction_time': float(prediction_time),
            'samples_evaluated': int(len(X_test))
        }
        
        # Print results
        print(f"\n📊 Performance Metrics:")
        print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
        print(f"\n⚡ Latency:")
        print(f"  Average:   {avg_latency:.4f} ms/sample")
        print(f"  Total:     {prediction_time:.4f} seconds")
        
        # Classification report
        if self.label_encoder:
            target_names = self.label_encoder.classes_
        else:
            target_names = [f"Class_{i}" for i in np.unique(y_test)]
        
        print(f"\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        self.plot_confusion_matrix(cm, target_names, model_name)
        
        return self.results[model_name]
    
    def plot_confusion_matrix(self, cm, class_names, model_name):
        """Plot confusion matrix"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=class_names, yticklabels=class_names)
        plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        os.makedirs('results', exist_ok=True)
        filepath = f'results/confusion_matrix_{model_name}.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Confusion matrix saved: {filepath}")
        plt.close()
    
    def compare_models(self):
        """Compare all evaluated models"""
        if not self.results:
            print("⚠ No models evaluated yet")
            return
        
        print(f"\n{'='*60}")
        print("Model Comparison")
        print('='*60)
        
        # Create comparison DataFrame
        df = pd.DataFrame(self.results).T
        df = df.round(4)
        
        print("\n", df.to_string())
        
        # Find best model
        best_model = df['accuracy'].idxmax()
        best_accuracy = df.loc[best_model, 'accuracy']
        best_latency = df.loc[best_model, 'avg_latency_ms']
        
        print(f"\n🏆 Best Model: {best_model}")
        print(f"   Accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
        print(f"   Latency:  {best_latency:.4f} ms")
        
        # Check if meets requirements
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
        
        # Plot comparison
        self.plot_model_comparison(df)
        
        return df
    
    def plot_model_comparison(self, df):
        """Plot model comparison charts"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        titles = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        
        for idx, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[idx // 2, idx % 2]
            df[metric].plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_ylabel('Score', fontsize=10)
            ax.set_xlabel('Model', fontsize=10)
            ax.set_ylim([0, 1.1])
            ax.grid(axis='y', alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for container in ax.containers:
                ax.bar_label(container, fmt='%.3f', padding=3)
        
        plt.tight_layout()
        filepath = 'results/model_comparison.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Model comparison plot saved: {filepath}")
        plt.close()
    
    def save_results(self, filepath='results/evaluation_results.json'):
        """Save evaluation results to JSON"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=4)
        print(f"✓ Results saved: {filepath}")

if __name__ == "__main__":
    print("Model Evaluation Module")
    print("This module is used by the main evaluation pipeline")
