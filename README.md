# AI-Powered Intrusion Detection System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Accuracy](https://img.shields.io/badge/accuracy-98.8%25-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A real-time AI-based Network Intrusion Detection System (NIDS) that monitors live network traffic and automatically classifies it as normal or one of four attack types — with 98.8% accuracy and under 0.005ms detection latency.

---

## How It Works

1. Scapy captures live network packets from your machine
2. Packets are grouped into flows and 14 features are extracted
3. Features are scaled and fed into a trained Random Forest model
4. Result is pushed instantly to a live web dashboard
5. If an attack is detected — toast notification + sound alert fires

---

## Attack Categories Detected

| Category | Description | Examples |
|---|---|---|
| normal | Legitimate traffic | Browsing, file transfers |
| dos | Denial of Service | Neptune, Smurf, DDoS, Hulk |
| probe | Scanning / Reconnaissance | Nmap, PortScan, Satan |
| r2l | Remote to Local intrusion | FTP-Patator, SSH-Patator |
| u2r | Privilege escalation | Buffer overflow, Rootkit |

---

## Model Results

| Model | Accuracy | F1-Score | Latency |
|---|---|---|---|
| Random Forest | 98.80% | 98.78% | 0.005ms |
| XGBoost | 98.80% | 98.79% | 0.004ms |
| Neural Network | 95.88% | 95.79% | 0.028ms |
| SVM | 85.96% | 82.22% | 0.267ms |

Trained on 2,976,194 samples from NSL-KDD + CIC-IDS2017 combined.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Npcap (Windows — required for live packet capture)
Download from https://npcap.com/#download
During install, check "Install Npcap in WinPcap API-compatible Mode"

### 3. Run the dashboard (as Administrator)
```bash
python app.py
```

### 4. Open in browser
```
http://127.0.0.1:5000
```

The dashboard will immediately start showing live detections. Real network packets are captured and classified alongside simulated attack patterns so all attack types are demonstrated.

---

## Project Structure

```
├── app.py                      # Flask server + live packet capture + SSE stream
├── main.py                     # Full training pipeline
├── download_dataset.py         # Download NSL-KDD + CIC-IDS2017
├── generate_report.py          # Generate PDF report
├── requirements.txt
├── templates/
│   └── index.html              # Live dashboard UI
├── notebooks/
│   └── IDS_Analysis.ipynb      # Jupyter notebook — EDA, model evaluation, charts
├── src/
│   ├── data_preprocessing.py   # Load & combine datasets
│   ├── model_training.py       # Train all 4 models
│   ├── model_evaluation.py     # Evaluate & compare models
│   ├── feature_engineering.py  # Feature importance analysis
│   ├── real_time_detection.py  # Standalone detection script
│   └── utils.py
├── models/                     # Trained models (included)
│   ├── random_forest.pkl
│   ├── xgboost.pkl
│   ├── svm.pkl
│   ├── neural_network.h5
│   └── preprocessor.pkl
├── data/
│   ├── KDDTrain+.txt
│   └── KDDTest+.txt
└── results/                    # Confusion matrices, charts, logs
```

---

## Jupyter Notebook

For data analysis and model evaluation:

```bash
pip install notebook
python -m notebook
```

Then open `notebooks/IDS_Analysis.ipynb` and run all cells. Covers dataset exploration, label distribution charts, feature analysis, confusion matrices, and feature importance.

---

## Retrain Models (optional)

If you want to retrain from scratch:

```bash
python download_dataset.py   # downloads CIC-IDS2017 (~370MB)
python main.py               # trains all 4 models
```

---

## Virtual Lab Testing (Parrot + Metasploitable 2)

To test with real attack traffic using VMware:

1. Set both VMs to Host-Only network adapter
2. Run `python app.py` as Administrator on your Windows host
3. From Parrot, run attacks against Metasploitable 2:

```bash
# Probe (port scan)
nmap -sS <metasploitable-ip>

# DoS
hping3 -S --flood <metasploitable-ip>

# R2L (brute force)
hydra -l msfadmin -P /usr/share/wordlists/rockyou.txt ssh://<metasploitable-ip>
```

The dashboard will detect and classify the attacks in real time.

---

## Datasets

- NSL-KDD — 148,517 samples, classic IDS benchmark
- CIC-IDS2017 — 2,827,677 samples, University of New Brunswick
- Combined — 2,976,194 samples, mapped to 14 common features

---

## Technologies

Python, scikit-learn, XGBoost, TensorFlow/Keras, Scapy, Flask, Chart.js, pandas, numpy, ReportLab

---

## Requirements

- Python 3.8+
- Windows (for live capture: Npcap + run as Administrator)
- 4GB+ RAM
- 2GB+ disk space

---

## Future Work

- AI-powered attack explanation — integrate an LLM (Groq/LLaMA) to generate SOC-style human-readable explanations when an attack is detected, including severity assessment and mitigation steps
- Controlled attack lab — integrate CICFlowMeter for real live attack detection using the exact same feature format the model was trained on
- SMOTE oversampling to fix class imbalance for R2L and U2R categories
- Add more datasets (UNSW-NB15, CIC-IDS2018) for broader attack coverage
- Store detections in a database for historical analysis
- Email/SMS alerting for critical detections
- Deploy on a dedicated network sensor or Raspberry Pi
- Ensemble voting across all 4 models for higher confidence predictions

---

Final Year Project — Computer Security

---

👩‍💻 Author:
 Silwalkg
 Cybersecurity Advanced Project | IT
