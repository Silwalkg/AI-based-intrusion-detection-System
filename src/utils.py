"""
Utility functions for the IDS system
"""
import os
import json
import pickle
import numpy as np
from datetime import datetime

def create_directories():
    """Create necessary directories for the project"""
    dirs = ['data', 'models', 'results', 'notebooks']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
    print("✓ Directories created successfully")

def save_model(model, model_name, model_dir='models'):
    """Save trained model to disk"""
    os.makedirs(model_dir, exist_ok=True)
    filepath = os.path.join(model_dir, f'{model_name}.pkl')
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    print(f"✓ Model saved: {filepath}")

def load_model(model_name, model_dir='models'):
    """Load trained model from disk"""
    filepath = os.path.join(model_dir, f'{model_name}.pkl')
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    print(f"✓ Model loaded: {filepath}")
    return model

def save_results(results, filename, results_dir='results'):
    """Save evaluation results to JSON"""
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"✓ Results saved: {filepath}")

def log_message(message, log_file='results/training.log'):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    with open(log_file, 'a') as f:
        f.write(log_entry)
    print(log_entry.strip())
