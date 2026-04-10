"""Flask dashboard server for AI-Powered IDS
Captures real network traffic via scapy, falls back to simulation if no admin rights."""
import sys, os, json, time, threading, pickle, sqlite3
sys.path.append('src')

import numpy as np
from flask import Flask, render_template, Response, jsonify
from collections import deque, defaultdict
from datetime import datetime

app = Flask(__name__)

# ── Global state ──────────────────────────────────────────────
detections  = deque(maxlen=100)
stats = {
    'total': 0,
    'attacks': 0,
    'breakdown': {'normal': 0, 'dos': 0, 'probe': 0, 'r2l': 0, 'u2r': 0},
    'latencies': deque(maxlen=200),
}
sse_clients = []
lock        = threading.Lock()

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

# ── SQLite database ───────────────────────────────────────────
DB_PATH = 'detections.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS detections (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp   TEXT,
        attack_type TEXT,
        is_attack   INTEGER,
        confidence  REAL,
        latency_ms  REAL,
        source      TEXT
    )''')
    conn.commit()
    conn.close()

def save_detection(record):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''INSERT INTO detections
            (timestamp, attack_type, is_attack, confidence, latency_ms, source)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (record['timestamp'], record['attack_type'], int(record['is_attack']),
             record['confidence'], record['latency_ms'], record['source']))
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()
print("✓ Database ready (detections.db)")

# ── Flow tracker for real traffic ────────────────────────────
flow_table = defaultdict(lambda: {
    'start': None, 'fwd_pkts': 0, 'bwd_pkts': 0,
    'fwd_bytes': 0, 'bwd_bytes': 0,
    'fwd_lens': [], 'syn': 0, 'rst': 0,
    'fwd_iats': [], 'bwd_iats': [],
    'fwd_hdr_len': 0, 'bwd_hdr_len': 0,
    'last_fwd': None, 'last_bwd': None,
})
flow_lock    = threading.Lock()
packet_id    = 0
FLOW_TIMEOUT = 5

def extract_features(flow):
    duration     = (flow['last_fwd'] or flow['start']) - flow['start']
    src_bytes    = flow['fwd_bytes']
    dst_bytes    = flow['bwd_bytes']
    count        = flow['fwd_pkts'] + flow['bwd_pkts']
    fwd_iats     = flow['fwd_iats']
    bwd_iats     = flow['bwd_iats']
    serror_rate  = np.mean(fwd_iats) if fwd_iats else 0.0
    rerror_rate  = np.mean(bwd_iats) if bwd_iats else 0.0
    total        = max(count, 1)
    same_srv     = flow['fwd_pkts'] / total
    diff_srv     = flow['bwd_pkts'] / total
    dst_h_count  = flow['bwd_pkts']
    dst_h_srv    = max(flow['fwd_lens']) if flow['fwd_lens'] else 0
    dst_h_same   = flow['fwd_hdr_len']
    dst_h_diff   = flow['bwd_hdr_len']
    dst_h_serr   = flow['syn'] / total
    dst_h_rerr   = flow['rst'] / total
    return [duration, src_bytes, dst_bytes, count,
            serror_rate, rerror_rate, same_srv, diff_srv,
            dst_h_count, dst_h_srv, dst_h_same, dst_h_diff,
            dst_h_serr, dst_h_rerr]

def classify_and_push(features, source='live'):
    global packet_id
    sample  = np.array(features, dtype=np.float32).reshape(1, -1)
    sample  = np.clip(sample, 0, None)
    t0      = time.time()
    scaled  = scaler.transform(sample)
    pred    = model.predict(scaled)[0]
    proba   = model.predict_proba(scaled)[0]
    latency = (time.time() - t0) * 1000

    attack_type = label_encoder.inverse_transform([pred])[0]
    confidence  = float(np.max(proba))
    is_attack   = attack_type != 'normal'

    with lock:
        packet_id += 1
        pid = packet_id

    record = {
        'id':          pid,
        'timestamp':   datetime.now().strftime('%H:%M:%S.%f')[:-3],
        'attack_type': attack_type,
        'is_attack':   is_attack,
        'confidence':  round(confidence, 3),
        'latency_ms':  round(latency, 4),
        'source':      source,
    }

    with lock:
        detections.appendleft(record)
        stats['total']  += 1
        if is_attack:
            stats['attacks'] += 1
        stats['breakdown'][attack_type] += 1
        stats['latencies'].append(latency)
        msg = f"data: {json.dumps(record)}\n\n"
        for q in list(sse_clients):
            try:
                q.append(msg)
            except Exception:
                pass

    threading.Thread(target=save_detection, args=(record,), daemon=True).start()

# ── Real packet capture (scapy) ──────────────────────────────
def packet_callback(pkt):
    try:
        from scapy.layers.inet import IP, TCP, UDP
        if not pkt.haslayer(IP):
            return
        ip    = pkt[IP]
        now   = time.time()
        proto = pkt.proto
        sport = pkt[TCP].sport if pkt.haslayer(TCP) else (pkt[UDP].sport if pkt.haslayer(UDP) else 0)
        dport = pkt[TCP].dport if pkt.haslayer(TCP) else (pkt[UDP].dport if pkt.haslayer(UDP) else 0)
        key   = (ip.src, sport, ip.dst, dport, proto)

        with flow_lock:
            f = flow_table[key]
            if f['start'] is None:
                f['start'] = now
            pkt_len = len(pkt)
            if f['fwd_pkts'] == 0 or sport == list(flow_table.keys())[0][1]:
                if f['last_fwd'] is not None:
                    f['fwd_iats'].append(now - f['last_fwd'])
                f['last_fwd']   = now
                f['fwd_pkts']  += 1
                f['fwd_bytes'] += pkt_len
                f['fwd_lens'].append(pkt_len)
                if pkt.haslayer(TCP):
                    f['fwd_hdr_len'] += pkt[TCP].dataofs * 4
            else:
                if f['last_bwd'] is not None:
                    f['bwd_iats'].append(now - f['last_bwd'])
                f['last_bwd']   = now
                f['bwd_pkts']  += 1
                f['bwd_bytes'] += pkt_len
                if pkt.haslayer(TCP):
                    f['bwd_hdr_len'] += pkt[TCP].dataofs * 4
            if pkt.haslayer(TCP):
                flags = pkt[TCP].flags
                if flags & 0x02: f['syn'] += 1
                if flags & 0x04: f['rst'] += 1
            duration = now - f['start']
            if duration >= FLOW_TIMEOUT or f['fwd_pkts'] + f['bwd_pkts'] >= 20:
                features = extract_features(f)
                del flow_table[key]
                threading.Thread(target=classify_and_push,
                                 args=(features, 'live'), daemon=True).start()
    except Exception:
        pass

def start_capture():
    try:
        from scapy.all import sniff
        print("✓ Starting real network capture...")
        sniff(prn=packet_callback, store=False, filter="ip")
    except Exception as e:
        print(f"⚠ Packet capture failed: {e}")
        print("  → Run as Administrator for real traffic capture")

# ── Simulation (always runs alongside real capture) ───────────
def make_normal():
    return [10862383+np.random.randint(0,1000000), 1027+np.random.randint(0,500),
            18534+np.random.randint(0,5000), 11+np.random.randint(0,5),
            1844378+np.random.randint(0,100000), 1729369+np.random.randint(0,100000),
            62626+np.random.randint(0,5000), 1711198+np.random.randint(0,100000),
            16+np.random.randint(0,5), 229+np.random.randint(0,20),
            0.0, 0.0, 0.05, 0.0]

def make_dos():
    return [98306075+np.random.randint(0,5000000), 370+np.random.randint(0,200),
            11595+np.random.randint(0,2000), 6+np.random.randint(0,4),
            19700000+np.random.randint(0,1000000), 16400000+np.random.randint(0,1000000),
            0.13+np.random.rand()*0.05, 121+np.random.randint(0,20),
            7+np.random.randint(0,3), 352+np.random.randint(0,30),
            164+np.random.randint(0,20), 232+np.random.randint(0,20), 0.0, 0.0]

def make_probe():
    return [47+np.random.randint(0,100), 0, 6+np.random.randint(0,10),
            1+np.random.randint(0,3), 0.0, 0.0,
            42553+np.random.randint(0,5000), 127659+np.random.randint(0,10000),
            1+np.random.randint(0,2), 0, 40+np.random.randint(0,10),
            20+np.random.randint(0,5), 0.0, 0.0]

def make_r2l():
    return [0.0, 12+np.random.randint(0,10), 0.0, 2+np.random.randint(0,3),
            0.0, 0.0, 1.0, 0.0,
            7+np.random.randint(0,5), 4+np.random.randint(0,3),
            0.57+np.random.rand()*0.1, 0.29+np.random.rand()*0.1, 0.0, 0.0]

def make_u2r():
    return [5006127+np.random.randint(0,500000), 447+np.random.randint(0,100),
            530+np.random.randint(0,100), 4+np.random.randint(0,2),
            1904+np.random.randint(0,500), 1668665+np.random.randint(0,100000),
            1.6+np.random.rand()*0.5, 195+np.random.randint(0,20),
            4+np.random.randint(0,2), 447+np.random.randint(0,50),
            136+np.random.randint(0,20), 136+np.random.randint(0,20), 0.0, 0.0]

generators = [make_normal, make_dos, make_probe, make_r2l, make_u2r]
weights    = [0.20, 0.35, 0.25, 0.12, 0.08]

def simulation_loop():
    while True:
        gen     = np.random.choice(generators, p=weights)
        sample  = np.array(gen(), dtype=np.float32)
        sample += np.random.normal(0, 0.01, size=len(sample))
        classify_and_push(sample.tolist(), source='simulated')
        time.sleep(0.5)

# ── Start detection threads ───────────────────────────────────
threading.Thread(target=start_capture, daemon=True).start()
threading.Thread(target=simulation_loop, daemon=True).start()

# ── Routes ────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    with lock:
        lats = list(stats['latencies'])
        return jsonify({
            'total':       stats['total'],
            'attacks':     stats['attacks'],
            'breakdown':   dict(stats['breakdown']),
            'avg_latency': round(sum(lats)/len(lats), 4) if lats else 0,
        })

@app.route('/api/feed')
def api_feed():
    with lock:
        return jsonify(list(detections))

@app.route('/api/stream')
def api_stream():
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

@app.route('/api/inject', methods=['POST'])
def api_inject():
    """Receives attack feature vectors from a remote machine.
    POST JSON: {"features": [...14 numbers...], "source": "network_attacker"}
    The IDS classifies them and pushes to the live dashboard."""
    from flask import request
    try:
        data     = request.get_json(force=True)
        features = data.get('features', [])
        source   = data.get('source', 'remote_attacker')
        if len(features) != 14:
            return jsonify({'error': f'Expected 14 features, got {len(features)}'}), 400
        threading.Thread(target=classify_and_push,
                         args=(features, source), daemon=True).start()
        return jsonify({'status': 'ok', 'features_received': len(features)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ping')
def api_ping():
    """Health check — confirms IDS is reachable."""
    return jsonify({'status': 'IDS online', 'model': 'random_forest'})

@app.route('/api/history')
def api_history():
    """Return last 500 detections from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute('''SELECT id, timestamp, attack_type, is_attack,
                               confidence, latency_ms, source
                               FROM detections ORDER BY id DESC LIMIT 500''').fetchall()
        conn.close()
        return jsonify([{
            'id': r[0], 'timestamp': r[1], 'attack_type': r[2],
            'is_attack': bool(r[3]), 'confidence': r[4],
            'latency_ms': r[5], 'source': r[6]
        } for r in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/attacks')
def api_history_attacks():
    """Return only attack detections from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute('''SELECT id, timestamp, attack_type, confidence, latency_ms, source
                               FROM detections WHERE is_attack=1
                               ORDER BY id DESC LIMIT 200''').fetchall()
        conn.close()
        return jsonify([{
            'id': r[0], 'timestamp': r[1], 'attack_type': r[2],
            'confidence': r[3], 'latency_ms': r[4], 'source': r[5]
        } for r in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n🛡  IDS Dashboard running at http://127.0.0.1:5000")
    print("   Run as Administrator for real network traffic capture\n")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
