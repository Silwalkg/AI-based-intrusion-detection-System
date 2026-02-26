# Quick Start Guide

Get your AI-Powered IDS up and running in 5 minutes!

## Prerequisites
- Python 3.8+ installed
- pip package manager
- Internet connection (for dataset download)

## Step-by-Step Setup

### 1. Install Dependencies (2 minutes)
```bash
pip install -r requirements.txt
```

### 2. Download Dataset (1 minute)
```bash
python download_dataset.py
```

Or manually download from: https://github.com/defcom17/NSL_KDD

### 3. Test Installation (30 seconds)
```bash
python test_system.py
```

This verifies all packages and files are correctly installed.

### 4. Train Models (10-30 minutes)
```bash
python main.py
```

This will:
- Preprocess the NSL-KDD dataset
- Train 4 ML models (Random Forest, XGBoost, SVM, Neural Network)
- Evaluate and compare all models
- Generate performance reports and visualizations

### 5. Test Real-Time Detection (30 seconds)
```bash
python src/real_time_detection.py
```

## What You'll Get

After training, you'll have:

### Trained Models
- `models/random_forest.pkl` - Best for accuracy
- `models/xgboost.pkl` - Best for speed
- `models/svm.pkl` - Good baseline
- `models/neural_network.h5` - Deep learning approach
- `models/preprocessor.pkl` - Data preprocessor

### Performance Reports
- `results/evaluation_results.json` - Detailed metrics
- `results/model_comparison.png` - Visual comparison
- `results/feature_importance.png` - Top features
- `results/confusion_matrix_*.png` - Per-model matrices
- `results/training.log` - Training logs

## Expected Performance

| Metric | Target | Typical Result |
|--------|--------|----------------|
| Accuracy | ≥95% | 98-99% |
| Latency | <50ms | 2-10ms |
| Attack Detection | All types | DoS, Probe, U2R, R2L |

## Quick Commands

```bash
# Full pipeline
python main.py

# Exploratory analysis
python notebooks/exploratory_analysis.py

# Real-time detection
python src/real_time_detection.py

# System test
python test_system.py

# Download dataset
python download_dataset.py
```

## Troubleshooting

### "Dataset not found"
Run: `python download_dataset.py`

### "Module not found"
Run: `pip install -r requirements.txt`

### "Out of memory"
Reduce SVM sample size in `src/model_training.py` (line 85)

### Slow training
This is normal for large datasets. Consider:
- Using a faster machine
- Reducing hyperparameter tuning
- Training fewer models

## Next Steps

1. ✓ Review results in `results/` directory
2. ✓ Check model comparison chart
3. ✓ Test real-time detection
4. ✓ Read full documentation in `DOCUMENTATION.md`
5. ✓ Customize for your use case

## Need Help?

- Read `SETUP_GUIDE.md` for detailed setup
- Check `DOCUMENTATION.md` for technical details
- Review `PROJECT_REPORT_TEMPLATE.md` for project structure

## Project Structure

```
├── data/                      # Dataset files
├── src/                       # Source code
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   ├── real_time_detection.py
│   └── utils.py
├── models/                    # Trained models
├── results/                   # Evaluation results
├── notebooks/                 # Analysis scripts
├── main.py                    # Main training pipeline
├── requirements.txt           # Dependencies
└── README.md                  # Project overview
```

## Success Criteria

Your system is working correctly if:
- ✓ All tests pass (`python test_system.py`)
- ✓ Models train without errors
- ✓ Accuracy ≥95%
- ✓ Latency <50ms
- ✓ All attack types detected

Happy detecting! 🛡️
