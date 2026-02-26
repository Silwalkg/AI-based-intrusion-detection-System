# Setup Guide - AI-Powered IDS

## Prerequisites
- Python 3.8 or higher
- pip package manager
- 4GB+ RAM recommended
- 2GB+ disk space for datasets

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download NSL-KDD Dataset

Option A: Direct Download
1. Visit: https://www.unb.ca/cic/datasets/nsl.html
2. Download NSL-KDD dataset
3. Extract and place these files in `data/` directory:
   - `KDDTrain+.txt`
   - `KDDTest+.txt`

Option B: GitHub Repository
```bash
# Clone the dataset repository
git clone https://github.com/defcom17/NSL_KDD.git
# Copy files to data directory
copy NSL_KDD\KDDTrain+.txt data\
copy NSL_KDD\KDDTest+.txt data\
```

### 3. Verify Setup
Check that your directory structure looks like this:
```
project/
├── data/
│   ├── KDDTrain+.txt
│   └── KDDTest+.txt
├── src/
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   ├── real_time_detection.py
│   └── utils.py
├── main.py
└── requirements.txt
```

## Running the Project

### Step 1: Exploratory Data Analysis (Optional)
```bash
python notebooks/exploratory_analysis.py
```

### Step 2: Train Models
```bash
python main.py
```
This will:
- Preprocess the dataset
- Engineer features
- Train 4 ML models (Random Forest, XGBoost, SVM, Neural Network)
- Evaluate all models
- Generate comparison reports

Expected runtime: 10-30 minutes depending on hardware

### Step 3: Real-Time Detection
```bash
python src/real_time_detection.py
```

## Troubleshooting

### Issue: Dataset not found
- Ensure files are in `data/` directory
- Check file names match exactly: `KDDTrain+.txt` and `KDDTest+.txt`

### Issue: Memory error
- Reduce SVM sample size in `model_training.py`
- Close other applications
- Use a machine with more RAM

### Issue: Import errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Issue: Slow training
- This is normal for large datasets
- Consider using GPU for Neural Network training
- Reduce hyperparameter tuning iterations

## Expected Outputs

After successful training, you'll find:

### Models (models/)
- `random_forest.pkl` - Random Forest classifier
- `xgboost.pkl` - XGBoost classifier
- `svm.pkl` - SVM classifier
- `neural_network.h5` - Neural Network model
- `preprocessor.pkl` - Data preprocessor

### Results (results/)
- `evaluation_results.json` - Performance metrics
- `model_comparison.png` - Model comparison chart
- `feature_importance.png` - Feature importance plot
- `confusion_matrix_*.png` - Confusion matrices
- `training.log` - Training logs

## Performance Targets

The system aims to achieve:
- ✓ Accuracy: ≥95%
- ✓ Latency: <50ms per prediction
- ✓ Attack Detection: DoS, Probe, U2R, R2L

## Next Steps

1. Review evaluation results
2. Select best performing model
3. Test with real network traffic
4. Deploy to production environment
5. Monitor and retrain periodically
