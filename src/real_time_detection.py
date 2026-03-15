"""
Real-time intrusion detection system
"""
import numpy as np
import time
import pickle
from collections import deque
from datetime import datetime

class RealTimeIDS:
    def __init__(self, model_path, preprocessor_path):
        """Initialize real-time IDS"""
        print("Initializing Real-Time IDS...")
        
        # Load model
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        print(f"✓ Model loaded: {model_path}")
        
        # Load preprocessor
        with open(preprocessor_path, 'rb') as f:
            preprocessor_data = pickle.load(f)
            self.scaler = preprocessor_data['scaler']
            self.label_encoder = preprocessor_data['label_encoder']
            self.feature_names = preprocessor_data['feature_names']
        print(f"✓ Preprocessor loaded: {preprocessor_path}")
        
        # Detection statistics
        self.detection_count = {label: 0 for label in self.label_encoder.classes_}
        self.total_detections = 0
        self.latency_history = deque(maxlen=1000)
        
        print("✓ Real-Time IDS initialized successfully")
    
    def preprocess_traffic(self, traffic_data):
        """Preprocess network traffic data"""
        # Ensure correct feature order
        if isinstance(traffic_data, dict):
            traffic_array = np.array([traffic_data.get(feat, 0) for feat in self.feature_names])
        else:
            traffic_array = np.array(traffic_data)
        
        # Reshape for single sample
        traffic_array = traffic_array.reshape(1, -1)
        
        # Scale features
        traffic_scaled = self.scaler.transform(traffic_array)
        
        return traffic_scaled
    
    def detect(self, traffic_data):
        """Detect intrusion in real-time"""
        start_time = time.time()
        
        # Preprocess
        X = self.preprocess_traffic(traffic_data)
        
        # Predict
        prediction = self.model.predict(X)[0]
        
        # Get prediction probability if available
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(X)[0]
            confidence = float(np.max(probabilities))
        else:
            confidence = 1.0
        
        # Calculate latency
        latency = (time.time() - start_time) * 1000  # ms
        self.latency_history.append(latency)
        
        # Decode prediction
        attack_type = self.label_encoder.inverse_transform([prediction])[0]
        
        # Update statistics
        self.detection_count[attack_type] += 1
        self.total_detections += 1
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'attack_type': attack_type,
            'is_attack': attack_type != 'normal',
            'confidence': confidence,
            'latency_ms': latency
        }
        
        return result
    
    def detect_batch(self, traffic_batch):
        """Detect intrusions in batch"""
        results = []
        start_time = time.time()
        
        # Preprocess batch
        X_batch = []
        for traffic in traffic_batch:
            X = self.preprocess_traffic(traffic)
            X_batch.append(X[0])
        
        X_batch = np.array(X_batch)
        
        # Predict batch
        predictions = self.model.predict(X_batch)
        
        # Get probabilities if available
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(X_batch)
            confidences = np.max(probabilities, axis=1)
        else:
            confidences = np.ones(len(predictions))
        
        total_time = time.time() - start_time
        avg_latency = (total_time / len(traffic_batch)) * 1000
        
        # Process results
        for pred, conf in zip(predictions, confidences):
            attack_type = self.label_encoder.inverse_transform([pred])[0]
            self.detection_count[attack_type] += 1
            self.total_detections += 1
            
            results.append({
                'attack_type': attack_type,
                'is_attack': attack_type != 'normal',
                'confidence': float(conf),
                'latency_ms': avg_latency
            })
        
        return results
    
    def get_statistics(self):
        """Get detection statistics"""
        avg_latency = np.mean(self.latency_history) if self.latency_history else 0
        max_latency = np.max(self.latency_history) if self.latency_history else 0
        min_latency = np.min(self.latency_history) if self.latency_history else 0
        
        attack_rate = (self.total_detections - self.detection_count.get('normal', 0)) / max(self.total_detections, 1)
        
        stats = {
            'total_detections': self.total_detections,
            'detection_breakdown': dict(self.detection_count),
            'attack_rate': float(attack_rate),
            'latency': {
                'average_ms': float(avg_latency),
                'max_ms': float(max_latency),
                'min_ms': float(min_latency)
            }
        }
        
        return stats
    
    def print_statistics(self):
        """Print detection statistics"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("Real-Time Detection Statistics")
        print("="*60)
        print(f"\nTotal Detections: {stats['total_detections']}")
        print(f"Attack Rate: {stats['attack_rate']*100:.2f}%")
        
        print("\n📊 Detection Breakdown:")
        for attack_type, count in stats['detection_breakdown'].items():
            percentage = (count / stats['total_detections'] * 100) if stats['total_detections'] > 0 else 0
            print(f"  {attack_type:10s}: {count:6d} ({percentage:5.2f}%)")
        
        print("\n⚡ Latency Statistics:")
        print(f"  Average: {stats['latency']['average_ms']:.4f} ms")
        print(f"  Min:     {stats['latency']['min_ms']:.4f} ms")
        print(f"  Max:     {stats['latency']['max_ms']:.4f} ms")
        
        if stats['latency']['average_ms'] < 50:
            print("\n✅ Latency requirement met (<50ms)")
        else:
            print("\n⚠ Latency exceeds 50ms threshold")

def simulate_traffic(num_samples=100, num_features=14):
    """
    Simulate network traffic with realistic patterns per attack type.
    Features order matches COMMON_FEATURES:
      duration, src_bytes, dst_bytes, count,
      serror_rate, rerror_rate, same_srv_rate, diff_srv_rate,
      dst_host_count, dst_host_srv_count, dst_host_same_srv_rate,
      dst_host_diff_srv_rate, dst_host_serror_rate, dst_host_rerror_rate
    """
    print(f"\nSimulating {num_samples} network traffic samples...")

    def make_normal():
        return [0.1, 500, 300, 5, 0.0, 0.0, 0.9, 0.05, 10, 8, 0.9, 0.05, 0.0, 0.0]

    def make_dos():
        # High connection count, high serror_rate, large src_bytes
        return [0.0, 50000 + np.random.randint(0, 50000), 0,
                500 + np.random.randint(0, 500), 0.9 + np.random.rand()*0.1,
                0.0, 1.0, 0.0, 255, 255, 1.0, 0.0,
                0.9 + np.random.rand()*0.1, 0.0]

    def make_probe():
        # Many different services, zero bytes, very high diff_srv_rate, high count
        return [0.0, 0, 0,
                500 + np.random.randint(0, 255),
                0.0, 0.0, 0.0, 1.0, 255, 1, 0.0, 1.0, 0.0, 0.0]

    def make_r2l():
        # Based on actual R2L mean values from training data
        return [3994469 + np.random.randint(0, 100000),
                18865 + np.random.randint(0, 5000),
                4356 + np.random.randint(0, 1000),
                6 + np.random.randint(0, 5),
                454544 + np.random.randint(0, 10000),
                198197 + np.random.randint(0, 10000),
                50392 + np.random.randint(0, 5000),
                316110 + np.random.randint(0, 10000),
                37 + np.random.randint(0, 10),
                156 + np.random.randint(0, 20),
                204 + np.random.randint(0, 20),
                258 + np.random.randint(0, 20),
                0.18, 0.01]

    def make_u2r():
        # Very low count, specific byte patterns
        return [100 + np.random.randint(0, 500),
                2000 + np.random.randint(0, 3000),
                1000 + np.random.randint(0, 2000),
                1, 0.0, 0.0, 1.0, 0.0, 1, 1, 1.0, 0.0, 0.0, 0.0]

    generators = [make_normal, make_dos, make_probe, make_r2l, make_u2r]
    # Weighted to reflect real-world distribution
    weights = [0.50, 0.25, 0.15, 0.07, 0.03]

    traffic_samples = []
    for _ in range(num_samples):
        gen = np.random.choice(generators, p=weights)
        sample = np.array(gen(), dtype=np.float32)
        # Add small noise
        sample += np.random.normal(0, 0.01, size=len(sample))
        sample = np.clip(sample, 0, None)
        traffic_samples.append(sample)

    return traffic_samples

if __name__ == "__main__":
    print("="*60)
    print("Real-Time Intrusion Detection System")
    print("="*60)
    
    try:
        # Initialize IDS
        ids = RealTimeIDS(
            model_path='models/random_forest.pkl',
            preprocessor_path='models/preprocessor.pkl'
        )
        
        # Simulate traffic
        traffic_samples = simulate_traffic(100)
        
        print("\n🔍 Starting real-time detection...")
        for i, traffic in enumerate(traffic_samples):
            result = ids.detect(traffic)
            
            if result['is_attack']:
                print(f"[{i+1}] ⚠ ATTACK DETECTED: {result['attack_type']} "
                      f"(confidence: {result['confidence']:.2f}, "
                      f"latency: {result['latency_ms']:.4f}ms)")
        
        # Print statistics
        ids.print_statistics()
        
    except FileNotFoundError as e:
        print(f"\n⚠ Error: {e}")
        print("\nPlease train models first:")
        print("  python main.py")
