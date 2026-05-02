"""
Model training module with multiple ML algorithms
"""
"""
all 4 models are trained
"""
import numpy as np
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, cross_val_score
from xgboost import XGBClassifier
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os

class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.best_params = {}
        
    def train_random_forest(self, X_train, y_train, hyperparameter_tuning=False):
        """Train Random Forest classifier"""
        print("\n" + "="*60)
        print("Training Random Forest...")
        print("="*60)
        
        if hyperparameter_tuning:
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2]
            }
            rf = RandomForestClassifier(random_state=42, n_jobs=-1)
            grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
            
            start_time = time.time()
            grid_search.fit(X_train, y_train)
            training_time = time.time() - start_time
            
            self.models['random_forest'] = grid_search.best_estimator_
            self.best_params['random_forest'] = grid_search.best_params_
            print(f"✓ Best parameters: {grid_search.best_params_}")
        else:
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
            self.models['random_forest'] = rf
        
        print(f"✓ Training completed in {training_time:.2f} seconds")
        return self.models['random_forest']
    
    def train_xgboost(self, X_train, y_train, hyperparameter_tuning=False):
        """Train XGBoost classifier"""
        print("\n" + "="*60)
        print("Training XGBoost...")
        print("="*60)
        
        if hyperparameter_tuning:
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [6, 10],
                'learning_rate': [0.01, 0.1],
                'subsample': [0.8, 1.0]
            }
            xgb = XGBClassifier(random_state=42, n_jobs=-1, eval_metric='mlogloss')
            grid_search = GridSearchCV(xgb, param_grid, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
            
            start_time = time.time()
            grid_search.fit(X_train, y_train)
            training_time = time.time() - start_time
            
            self.models['xgboost'] = grid_search.best_estimator_
            self.best_params['xgboost'] = grid_search.best_params_
            print(f"✓ Best parameters: {grid_search.best_params_}")
        else:
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
            self.models['xgboost'] = xgb
        
        print(f"✓ Training completed in {training_time:.2f} seconds")
        return self.models['xgboost']
    
    def train_svm(self, X_train, y_train, sample_size=10000):
        """Train SVM classifier (on subset due to computational cost)"""
        print("\n" + "="*60)
        print("Training SVM...")
        print("="*60)
        
        # Use subset for SVM due to computational cost
        if len(X_train) > sample_size:
            print(f"⚠ Using {sample_size} samples for SVM training (computational efficiency)")
            indices = np.random.choice(len(X_train), sample_size, replace=False)
            X_train_subset = X_train[indices]
            y_train_subset = y_train[indices]
        else:
            X_train_subset = X_train
            y_train_subset = y_train
        
        svm = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
        
        start_time = time.time()
        svm.fit(X_train_subset, y_train_subset)
        training_time = time.time() - start_time
        
        self.models['svm'] = svm
        print(f"✓ Training completed in {training_time:.2f} seconds")
        return self.models['svm']
    
    def train_neural_network(self, X_train, y_train, X_val, y_val, num_classes):
        """Train Neural Network classifier"""
        print("\n" + "="*60)
        print("Training Neural Network...")
        print("="*60)
        
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print(model.summary())
        
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
        
        start_time = time.time()
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=30,
            batch_size=256,
            callbacks=[early_stopping],
            verbose=1
        )
        training_time = time.time() - start_time
        
        self.models['neural_network'] = model
        print(f"✓ Training completed in {training_time:.2f} seconds")
        return model, history
    
    def save_model(self, model_name, filepath=None):
        """Save trained model"""
        if model_name not in self.models:
            print(f"⚠ Model {model_name} not found")
            return
        
        os.makedirs('models', exist_ok=True)
        
        if filepath is None:
            filepath = f'models/{model_name}.pkl'
        
        if model_name == 'neural_network':
            self.models[model_name].save(f'models/{model_name}.h5')
            print(f"✓ Neural Network saved: models/{model_name}.h5")
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(self.models[model_name], f)
            print(f"✓ Model saved: {filepath}")
    
    def cross_validate(self, model_name, X, y, cv=5):
        """Perform cross-validation"""
        if model_name not in self.models:
            print(f"⚠ Model {model_name} not found")
            return None
        
        print(f"\nPerforming {cv}-fold cross-validation for {model_name}...")
        scores = cross_val_score(self.models[model_name], X, y, cv=cv, scoring='accuracy', n_jobs=-1)
        
        print(f"✓ Cross-validation scores: {scores}")
        print(f"✓ Mean accuracy: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
        
        return scores

if __name__ == "__main__":
    print("Model Training Module")
    print("This module is used by the main training pipeline")
