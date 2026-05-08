# Live Traffic Integration Guide

## Overview

The real-time detection module now supports live network traffic capture and analysis. Instead of just simulating attacks, you can monitor actual network traffic and detect intrusions in real-time.

## Architecture

### Components

1. **NetworkFlow** - Represents a network conversation
   - Tracks packets between two hosts
   - Extracts 14 features for ML model
   - Monitors error rates and byte counts

2. **PacketCapture** - Captures packets from network interface
   - Uses Scapy to sniff packets
   - Groups packets into flows
   - Runs in background thread
   - Cleans up inactive flows

3. **RealTimeIDS** - Main detection engine
   - Loads trained ML models
   - Processes flows from PacketCapture
   - Detects attacks in real-time
   - Maintains statistics

## How It Works

```
Network Interface
    ↓
Packet Capture (Scapy)
    ↓
Flow Extraction (group by IP/port)
    ↓
Feature Extraction (14 features)
    ↓
ML Model Detection
    ↓
Alert + Statistics
```

## Usage

### Basic Setup (Simulated Traffic)

```python
from src.real_time_detection import RealTimeIDS, simulate_traffic

# Initialize without interface (uses simulated data)
ids = RealTimeIDS(
    model_path='models/random_forest.pkl',
    preprocessor_path='models/preprocessor.pkl'
)

# Simulate traffic
traffic = simulate_traffic(100)

# Detect
for sample in traffic:
    result = ids.detect(sample)
    if result['is_attack']:
        print(f"Attack: {result['attack_type']}")
```

### Live Traffic Detection

```python
from src.real_time_detection import RealTimeIDS

# Initialize with network interface
ids = RealTimeIDS(
    model_path='models/random_forest.pkl',
    preprocessor_path='models/preprocessor.pkl',
    interface='eth0'  # or 'wlan0', 'en0', etc.
)

# Start live detection
ids.start_live_detection()

# Press Ctrl+C to stop
```

## Finding Your Network Interface

### Linux/Mac
```bash
ifconfig
# or
ip addr show
```

### Windows
```bash
ipconfig
```

### Python
```python
from scapy.all import get_if_list
print(get_if_list())
```

## Features Extracted from Flows

The system extracts these 14 features from each network flow:

1. **duration** - Flow duration in seconds
2. **src_bytes** - Bytes sent from source
3. **dst_bytes** - Bytes sent from destination
4. **count** - Number of packets
5. **src_error_rate** - Source error rate
6. **dst_error_rate** - Destination error rate
7. **same_srv_rate** - Same service rate
8. **diff_srv_rate** - Different service rate
9. **dst_host_count** - Destination host count
10. **dst_host_srv_count** - Destination host service count
11. **dst_host_same_srv_rate** - Same service rate for destination host
12. **dst_host_diff_srv_rate** - Different service rate for destination host
13. **dst_host_serror_rate** - Destination host error rate
14. **dst_host_rerror_rate** - Destination host reverse error rate

## Attack Detection

The system detects these attack types:

- **normal** - Legitimate traffic
- **DoS** - Denial of Service attacks
- **Probe** - Network reconnaissance/scanning
- **R2L** - Remote to Local attacks
- **U2R** - User to Root privilege escalation

## Testing with Another Laptop

You can test the system by sending attacks from another machine:

### From Attacker Machine (Laptop B)

```bash
# Port scan (Probe attack)
nmap -sV target_ip

# Ping flood (DoS attack)
ping -f target_ip

# TCP SYN flood (DoS attack)
hping3 -S --flood target_ip
```

### On IDS Machine (Laptop A)

```python
ids = RealTimeIDS(
    model_path='models/random_forest.pkl',
    preprocessor_path='models/preprocessor.pkl',
    interface='eth0'
)
ids.start_live_detection()
```

The IDS will detect and log attacks from Laptop B in real-time.

## Performance Considerations

- **CPU Usage**: Packet capture and feature extraction consume CPU
- **Memory**: Active flows stored in memory (default timeout: 30 seconds)
- **Latency**: Detection happens within milliseconds
- **Scalability**: High-traffic networks may require optimization

## Troubleshooting

### "Permission denied" error
Packet capture requires elevated privileges:

```bash
# Linux/Mac
sudo python3 your_script.py

# Windows (run as Administrator)
python your_script.py
```

### "No such device" error
Interface name is incorrect. Use `get_if_list()` to find available interfaces.

### No attacks detected
- Check that traffic is actually flowing on the interface
- Verify the ML model is trained correctly
- Check confidence thresholds

## Integration with Dashboard

The live detection can be integrated with the Flask dashboard:

```python
# In app.py
from src.real_time_detection import RealTimeIDS

ids = RealTimeIDS(
    model_path='models/random_forest.pkl',
    preprocessor_path='models/preprocessor.pkl',
    interface='eth0'
)

@app.route('/api/live-stats')
def live_stats():
    stats = ids.get_statistics()
    return jsonify(stats)
```

## Next Steps

1. Configure your network interface
2. Start live detection
3. Monitor the output
4. Integrate with dashboard for visualization
5. Set up email alerts for detected attacks
