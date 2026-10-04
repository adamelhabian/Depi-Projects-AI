# Part 2: Modeling & Optimization

This folder contains the machine learning modeling, cross-validation, and optimization for the Boston Housing project (`MEDV` price prediction).

---

## 📌 Overview

- **Input Features:** `RM`, `LSTAT`, `PTRATIO` (Float)
- **Target:** `MEDV` (House price in $)
- **Dataset:** 489 samples (80% Train: 391, 20% Test: 98)

---

## 🛠️ Models Tested

1. **Linear Regression**
2. **Polynomial Regression (Degree 3)**
3. **Ridge Regression**
4. **Lasso Regression**
5. **Decision Tree Regressor**
6. **Random Forest Regressor**
7. **Gradient Boosting Regressor**

---

## 📊 Summary of Results (5-Fold CV & Test Set)

| Model | CV Mean R² | CV Mean RMSE ($) | Test R² | Test RMSE ($) | Test MAE ($) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Polynomial Regression (Deg 3)** 🏆 | **0.8294** | **$69,065** | **0.8223** | **$62,498** | **$48,325** |
| **Gradient Boosting** | 0.8319 | $68,593 | 0.8481 | $57,779 | $44,488 |
| **Random Forest** | 0.8293 | $69,201 | - | - | - |
| **Decision Tree** | 0.8042 | $73,857 | - | - | - |
| **Ridge** | 0.7133 | $89,485 | - | - | - |
| **Lasso** | 0.7134 | $89,485 | - | - | - |
| **Linear Regression** | 0.7133 | $89,487 | - | - | - |

> **Final Choice:** **Polynomial Regression (Degree 3)** was chosen as the champion model because it gives virtually the same accuracy as complex ensemble models while being a single, fast mathematical model.

---

## 📁 Files in this Directory

- `MLPhase2.ipynb`: Main notebook covering data loading, CV, GridSearchCV, model comparison, test evaluation, and feature importance.
- `README.md`: This summary file.
