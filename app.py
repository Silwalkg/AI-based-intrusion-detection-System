"""
Flask dashboard server for AI-Powered IDS
"""
import sys, os, json, time, threading, pickle
sys.path.append('src')

import numpy as np
from flask import Flask, render_template, Response, jsonify
from collections import deque
from datetime import datetime

app = Flask(__name__)

# ── Global state ──────────────────────────────────────────────
detections   = deque(maxlen=100)   # last 100 detections for feed
stats = {
    'total': 0,
    'attacks': 0,
    'breakdown': {'normal': 0, 'dos': 0, 'probe': 0, 'r2l': 0, 'u2r': 0},
    'latencies': deque(maxlen=200),
}
sse_clients  = []
lock = threading.Lock()

# ── Load model & preprocessor ────────────────────────────────
print("Loading model...")
with open('models/random_forest.pkl', 'rb') as f:
    model = pickle.load(f)
with open('models/preprocessor.pkl', 'rb') as f:
    pp = pickle.load(f)
    scaler        = pp['scaler']
    label_encoder = pp['label_encoder']
    feature_names = pp['feature_names']
print("✓ Model ready")

# ── Traffic simulators (realistic per-class patterns) ─────────
def make_normal():
    return [0.1, 500, 300, 5, 0.0, 0.0, 0.9, 0.05, 10, 8, 0.9, 0.05, 0.0, 0.0]

def make_dos():
    return [0.0, 50000+np.random.randint(0,50000), 0,
            500+np.random.randint(0,500), 0.9+np.random.rand()*0.1,
            0.0, 1.0, 0.0, 255, 255, 1.0, 0.0,
            0.9+np.random.rand()*0.1, 0.0]

def make_probe():
    return [0.0, 0, 0, 500+np.random.randint(0,255),
            0.0, 0.0, 0.0, 1.0, 255, 1, 0.0, 1.0, 0.0, 0.0]

def make_r2l():
    return [3994469+np.random.randint(0,100000),
            18865+np.random.randint(0,5000), 4356+np.random.randint(0,1000),
            6+np.random.randint(0,5), 454544+np.random.randint(0,10000),
            198197+np.random.randint(0,10000), 50392+np.random.randint(0,5000),
            316110+np.random.randint(0,10000), 37+np.random.randint(0,10),
            156+np.random.randint(0,20), 204+np.random.randint(0,20),
            258+np.random.randint(0,20), 0.18, 0.01]

def make_u2r():
    return [100+np.random.randint(0,500), 2000+np.random.randint(0,3000),
            1000+np.random.randint(0,2000), 1, 0.0, 0.0, 1.0, 0.0, 1, 1, 1.0, 0.0, 0.0, 0.0]

generators = [make_normal, make_dos, make_probe, make_r2l, make_u2r]
weights    = [0.50, 0.25, 0.15, 0.07, 0.03]

# ── Detection loop (background thread) ───────────────────────
def detection_loop():
    packet_id = 0
    while True:
        gen    = np.random.choice(generators, p=weights)
        sample = np.array(gen(), dtype=np.float32)
        sample += np.random.normal(0, 0.01, size=len(sample))
        sample  = np.clip(sample, 0, None).reshape(1, -1)

        t0      = time.time()
        scaled  = scaler.transform(sample)
        pred    = model.predict(scaled)[0]
        proba   = model.predict_proba(scaled)[0]
        latency = (time.time() - t0) * 1000

        attack_type = label_encoder.inverse_transform([pred])[0]
        confidence  = float(np.max(proba))
        is_attack   = attack_type != 'normal'
        packet_id  += 1

        record = {
            'id':          packet_id,
            'timestamp':   datetime.now().strftime('%H:%M:%S.%f')[:-3],
            'attack_type': attack_type,
            'is_attack':   is_attack,
            'confidence':  round(confidence, 3),
            'latency_ms':  round(latency, 4),
        }

        with lock:
            detections.appendleft(record)
            stats['total'] += 1
            if is_attack:
                stats['attacks'] += 1
            stats['breakdown'][attack_type] += 1
            stats['latencies'].append(latency)

        # Push to all SSE clients
        msg = f"data: {json.dumps(record)}\n\n"
        with lock:
            for q in list(sse_clients):
                try:
                    q.append(msg)
                except Exception:
                    pass

        time.sleep(0.5)   # one packet every 500ms

threading.Thread(target=detection_loop, daemon=True).start()

# ── Routes ────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    with lock:
        lats = list(stats['latencies'])
        return jsonify({
            'total':     stats['total'],
            'attacks':   stats['attacks'],
            'breakdown': dict(stats['breakdown']),
            'avg_latency': round(sum(lats)/len(lats), 4) if lats else 0,
        })

@app.route('/api/feed')
def api_feed():
    with lock:
        return jsonify(list(detections))

@app.route('/api/stream')
def api_stream():
    """Server-Sent Events — pushes each detection to the browser in real-time."""
    client_queue = []
    with lock:
        sse_clients.append(client_queue)

    def generate():
        try:
            while True:
                if client_queue:
                    yield client_queue.pop(0)
                else:
                    yield ': keep-alive\n\n'
                    time.sleep(0.1)
        finally:
            with lock:
                if client_queue in sse_clients:
                    sse_clients.remove(client_queue)

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

if __name__ == '__main__':
    print("\n🛡  IDS Dashboard running at http://127.0.0.1:5000\n")
    app.run(debug=False, threaded=True)
