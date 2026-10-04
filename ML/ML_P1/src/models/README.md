# Trained Model Artifacts (for Backend API)

This folder contains the production artifacts for the **Boston Housing Price Prediction** system.

---

## 📦 Files

| File | Description | Input Expected |
| :--- | :--- | :--- |
| **`scaler.pkl`** | `StandardScaler` fitted on training data | 3 Raw features: `[[RM, LSTAT, PTRATIO]]` |
| **`model.pkl`** | Polynomial Regression model (includes degree-3 mapping) | Scaled features from `scaler.transform()` |
| **`pipeline.pkl`** | All-in-One Pipeline (Scaler + Poly + Model) | 3 Raw features: `[[RM, LSTAT, PTRATIO]]` |
| **`poly.pkl`** | Standalone `PolynomialFeatures(3, include_bias=False)` | Scaled features (optional) |

---

## 💻 Quick Usage in Backend (Python)

### Option 1: Two-Step (Scaler then Model)
```python
import pickle
import numpy as np

# Load files
with open('src/models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('src/models/model.pkl', 'rb') as f:
    model = pickle.load(f)

# Input from Frontend
raw_features = np.array([[6.5, 10.0, 15.3]])  # RM, LSTAT, PTRATIO

# Transform & Predict
scaled_features = scaler.transform(raw_features)
price = model.predict(scaled_features)[0]

print(f"Predicted Price: ${price:,.2f}")
```

### Option 2: One-Step (All-in-One Pipeline — Recommended)
```python
import pickle
import numpy as np

with open('src/models/pipeline.pkl', 'rb') as f:
    pipeline = pickle.load(f)

raw_features = np.array([[6.5, 10.0, 15.3]])
price = pipeline.predict(raw_features)[0]

print(f"Predicted Price: ${price:,.2f}")
```
