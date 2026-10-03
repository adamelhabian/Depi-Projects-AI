# Boston Housing ML Project — Source Modules (`src/`)

This directory contains the core source code, machine learning pipelines, preprocessing modules, model storage, and integration components for the Boston Housing Price Prediction system.

---

## 📁 Directory Structure

```
src/
├── preprocessing/          # Data preprocessing and cleaning pipeline
│   ├── preprocessing pipline.ipynb
│   └── scaler.joblib
│
├── ml/
│   ├── MLpart1/            # Part 1: Exploratory ML, baseline models & parameter sweeps
│   │   ├── mlP1.txt
│   │   └── MLPhase1.ipynb
│   │
│   └── MLpart2/            # Part 2: Modeling, 5-Fold CV, Hyperparameter Tuning & Selection
│       ├── README.md       # Detailed Part 2 documentation
│       └── MLPhase2.ipynb  # Executed Part 2 notebook
│
├── models/                 # Serialized production models for Backend deployment
│   └── .gitkeep
│
├── backend/                # Backend API service (FastAPI / Flask / Django)
│   └── .gitkeep
│
├── frontend/               # Frontend user interface dashboard
│   └── .gitkeep
│
└── requirements.txt        # Project dependencies
```

---

## 🚀 Getting Started

```bash
# Install required Python packages
pip install -r requirements.txt
```

### Module Links
- **Part 1 Notebook:** [`ml/MLpart1/MLPhase1.ipynb`](ml/MLpart1/MLPhase1.ipynb)
- **Part 2 Notebook:** [`ml/MLpart2/MLPhase2.ipynb`](ml/MLpart2/MLPhase2.ipynb)
- **Part 2 Documentation:** [`ml/MLpart2/README.md`](ml/MLpart2/README.md)
