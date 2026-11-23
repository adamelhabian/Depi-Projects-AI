# Machine Learning Engine — EduWise

This directory contains the machine learning pipelines, preprocessing modules, training workflows, model artifacts, and evaluation reports for the **EduWise** educational platform.

---

## 1. Overview and Implementation Status

The initial machine learning release delivers the **Academic Risk Prediction** pipeline alongside native **TreeSHAP Explainability** and **What-If Simulation**.

* **Primary Objective:** Identify students at risk of academic failure early in the semester, explain the underlying causes with exact mathematical attributions, and provide actionable interventions for teachers.
* **Winning Model:** `XGBClassifier` tuned with a decision threshold of **0.369** (selected over Logistic Regression and Random Forest via 5-fold cross-validation).
* **Holdout Performance (`metrics.json`):**
  * **ROC-AUC:** `0.941`
  * **Accuracy:** `88.5%`
  * **Recall:** `81.6%` (capturing over 81% of struggling students)
  * **Precision:** `77.3%`
  * **F1-Score:** `79.4%`
* **Explainability (TreeSHAP):** Local feature attributions calculated natively via `pred_contribs` without heavy external dependencies, extracting top risk factors and protective factors for each student.
* **Test Suite:** 16 automated unit tests covering data schemas, preprocessing transformations, pipeline serialization, inference contracts, and counterfactual simulation.

---

## 2. Dataset Guide for Team Members

The raw dataset is stored in `data/raw/student_academic_risk.csv` (3,000 synthetic Egyptian education center student profiles generated via `data/generate_academic_data.py`).

Here is how this dataset aligns with each planned machine learning feature:

| Planned Feature | Assigned Member | Status with Current Dataset | Guidance |
| :--- | :--- | :--- | :--- |
| **Academic Risk Prediction** | **Youssef** | **Ready & Implemented** | Fully fitted and evaluated against the `is_at_risk` target label. Model pipeline serialized in `models/saved_models/`. |
| **Student Segmentation** | **Maya** | **Ready to Use Immediately** | Unsupervised clustering (e.g., K-Means, DBSCAN) requires no target label. Maya can directly train on existing features: `attendance_rate`, `homework_completion_rate`, `average_quiz_score`, `midterm_score`, and `participation_score`. |
| **Dropout Risk Prediction** | **Tasbeeh** | **Features Ready (Needs Target)** | The student table already contains the core behavioral churn signals (`missed_sessions_count`, `fee_delayed_days`, `attendance_rate`). To train a supervised classifier, an `is_dropout` target column can be derived or appended via `generate_academic_data.py`. |
| **Revenue Forecasting** | **Team** | **Requires Separate Time-Series Data** | Student snapshot tables cannot train time-series models. This feature requires aggregated monthly center records (`date`, `active_students`, `tuition_revenue`, `expenses`, `net_profit`). |

---

## 3. Directory Structure

```text
src/machine_learning/
├── preprocessing/
│   ├── __init__.py
│   └── academic_risk_preprocessor.py   # Pydantic schema validation, feature engineering (quiz trends), imputer, scaler
├── models/
│   ├── __init__.py
│   ├── academic_risk_model.py          # Model container, metadata tracking, and serialization
│   └── saved_models/
│       └── academic_risk_pipeline.joblib # Production-ready trained XGBoost pipeline artifact
├── training/
│   ├── __init__.py
│   └── train_academic_risk.py          # 5-fold CV hyperparameter search across LR, RF, and XGBoost
├── evaluation/
│   ├── __init__.py
│   ├── evaluate_academic_risk.py       # Holdout evaluation script and confusion matrix generator
│   └── metrics.json                    # Serialized benchmark scores, parameters, and environment versions
└── README.md                           # Component documentation
```

---

## 4. Pipeline Execution Commands

Run all commands from the `Graduation Project/EduWise/` directory using Python 3.13:

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Generate raw synthetic cohort (3,000 students)
python -m data.generate_academic_data

# 3. Train models and select best artifact
python -m src.machine_learning.training.train_academic_risk

# 4. Evaluate on holdout test set and export metrics.json
python -m src.machine_learning.evaluation.evaluate_academic_risk

# 5. Run test suite
python -m pytest --basetemp=.pytest_temp tests/test_ml.py
```

---

## 5. Backend Service Usage

The trained pipeline is exposed via `AcademicRiskService` in `src/backend/services/academic_risk_service.py` for FastAPI endpoints:

```python
from src.backend.services.academic_risk_service import AcademicRiskService

service = AcademicRiskService()

# 1. Standard prediction
prediction = service.predict({
    "student_id": "EG-00101",
    "group_id": "G-02",
    "attendance_rate": 0.52,
    "homework_completion_rate": 0.40,
    "average_quiz_score": 45.0,
    "midterm_score": 48.0,
    "participation_score": 40.0,
    "missed_sessions_count": 3,
})

# 2. Explainable prediction with TreeSHAP
explanation = service.explain(student_dict)
# Returns:
# - risk_category: "High / Academic Risk"
# - top_risk_factors: e.g. [{"feature": "quiz_latest", "label_ar": "درجة آخر كويز", "impact": 2.24}, ...]
# - top_protective_factors: e.g. [{"feature": "homework_completion_rate", "impact": -0.45}, ...]
# - recommended_actions: Actionable teacher guidance in Arabic and English

# 3. What-If Counterfactual Simulation
sim = service.simulate_what_if(student_dict, improvements={
    "attendance_rate": 0.85,
    "quiz_latest": 75.0,
    "missed_sessions_count": 0,
})
# Returns baseline vs simulated probability, risk reduction, and rescued_from_risk status
```
