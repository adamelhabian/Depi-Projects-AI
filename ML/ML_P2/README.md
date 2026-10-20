# CharityML - Donor Intelligence & Income Prediction

An end-to-end Machine Learning web application designed to help charitable organizations identify prospective donors likely to earn more than $50,000 annually from demographic census data.

Developed as a collaborative project under the **Digital Egypt Pioneers Initiative (DEPI)** - Machine Learning Track.

---

## Live Deployment

* **Production Web App:** [https://depi-projects-ai-production-33b1.up.railway.app/](https://depi-projects-ai-production-33b1.up.railway.app/)
* **Platform:** Railway Cloud Platform
* **Backend:** FastAPI + Uvicorn ASGI Server
* **Frontend:** Responsive Semantic HTML5 & Modern CSS

---

## Project Overview

Non-profit organizations often rely on donor campaigns that require significant outreach expenses. Finding individuals who have the financial capacity to donate (typically individuals with an annual income greater than $50,000) maximizes campaign return on investment (ROI).

Using data extracted from the **1994 U.S. Census Bureau database**, CharityML implements a supervised learning classifier that analyzes individual demographic and economic profiles to accurately predict income brackets (`<=50K` vs `>50K`).

---

## Team & Roles

| Contributor | Role & Responsibilities |
| :--- | :--- |
| **Youssef Mohamed** | **Frontend Engineering & UI/UX Design**<br>Semantic HTML5 structure, modern responsive CSS tokens, zero-emoji UI, SVG vector icons, real-time client-side field synchronization, dynamic result card rendering. |
| **Mina** | **Backend Engineering & API Architecture**<br>FastAPI server implementation, Pydantic input schemas and data validation, asynchronous endpoint handling, model pipeline inference service. |
| **Adam Elhabian** | **Machine Learning & Model Integration**<br>Model training, hyperparameter tuning, model serialization (`joblib`), client-backend asynchronous fetch integration, deployment pipeline. |
| **Maya** | **Machine Learning & Model Evaluation**<br>Classifier experimentation, comparative evaluation (Random Forest, AdaBoost, Gradient Boosting, XGBoost), ROC-AUC and F-beta analysis. |
| **Tasbeeh Hassan** | **Data Analysis & Preprocessing**<br>Exploratory Data Analysis (EDA), missing value handling, skewed feature transformation (log scaling), categorical one-hot encoding, feature normalization. |

---

## System Architecture

```text
+-------------------------------------------------------------+
|                     Client Browser                          |
|  - Semantic HTML5 Interface                                 |
|  - Modern CSS (Custom Design System, Responsive Grid)       |
|  - Client-side validation & Education Level Sync            |
|  - Asynchronous Fetch API (JSON payload)                    |
+------------------------------+------------------------------+
                               |
                               | HTTP POST /predict (JSON)
                               v
+-------------------------------------------------------------+
|                   FastAPI Web Server                        |
|  - ASGI framework powered by Uvicorn                        |
|  - Pydantic Schema Validation (PredictionInput)             |
|  - Template Serving (Jinja2) & Static File Mounting         |
+------------------------------+------------------------------+
                               |
                               | pandas.DataFrame (13 features)
                               v
+-------------------------------------------------------------+
|              Machine Learning Inference Pipeline             |
|  - Preprocessor (preprocessor.pkl):                         |
|      * Log Transform (capital-gain, capital-loss)           |
|      * MinMax Scaling (continuous features)                 |
|      * One-Hot Encoding (categorical variables)             |
|  - Classifier (model.pkl):                                  |
|      * Trained XGBoost Classifier Model                     |
+------------------------------+------------------------------+
                               |
                               | JSON Result: {"income_category": ">50K", ...}
                               v
+-------------------------------------------------------------+
|                Dynamic UI Result Card Update                |
|  - Likely Donor Candidate (> $50K)  [Cobalt Highlight]      |
|  - Standard Income Tier (<= $50K)   [Neutral State]         |
+-------------------------------------------------------------+
```

---

## Machine Learning Pipeline & Results

### 1. Dataset
* **Source:** 1994 US Census Bureau (45,222 records after cleaning).
* **Target:** `income` binary label (`<=50K` -> `0`, `>50K` -> `1`).
* **Input Features:** 13 demographic and socio-economic attributes (`age`, `workclass`, `education_level`, `education-num`, `marital-status`, `occupation`, `relationship`, `race`, `sex`, `capital-gain`, `capital-loss`, `hours-per-week`, `native-country`).

### 2. Preprocessing
* **Skewed Feature Transformation:** Log transformation applied to highly skewed monetary features (`capital-gain` and `capital-loss`).
* **Numeric Scaling:** Continuous features normalized using `MinMaxScaler` to bring numerical values into a standard `[0, 1]` range.
* **Categorical Encoding:** One-hot encoding applied to nominal categorical variables.
* **Validation Strategy:** Stratified 80/20 train/test split preserving target class distribution.

### 3. Model Comparison & Metrics

Multiple ensemble classifiers were trained and benchmarked on the test set:

| Algorithm | Accuracy | Precision (`>50K`) | Recall (`>50K`) | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **XGBoost (Selected)** | **86.0%** | **0.79** | **0.58** | **0.67** | **0.9156** |
| **Gradient Boosting** | 86.0% | 0.78 | 0.58 | 0.67 | 0.9168 |
| **AdaBoost** | 85.0% | 0.76 | 0.57 | 0.65 | 0.9035 |
| **Random Forest** | 84.2% | 0.71 | 0.62 | 0.66 | 0.8899 |

**XGBoost** was chosen as the production model due to its high precision (0.79), strong overall accuracy, balanced F-score, and optimal inference latency.

---

## Technologies & Stack

* **Programming Language:** Python 3.10+
* **Data Processing & Machine Learning:**
  * pandas
  * NumPy
  * scikit-learn
  * XGBoost
  * joblib
* **Backend & API:**
  * FastAPI
  * Uvicorn
  * Pydantic v2
  * Jinja2
* **Frontend:**
  * Semantic HTML5
  * Vanilla CSS3 (Custom Design Tokens, Flexbox, CSS Grid)
  * Vanilla JavaScript (Fetch API, DOM manipulation)
  * SVG Vector Icons (No emoji dependencies)
  * Google Fonts (Inter)
* **DevOps & Deployment:**
  * Git & GitHub
  * Railway Cloud Platform

---

## Directory Structure

```text
ML_P2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py                     # FastAPI application & /predict endpoint
│   └── model/
│       ├── model.pkl                   # Trained XGBoost model artifact
│       └── preprocessor.pkl            # Scikit-learn data preprocessor pipeline
│
├── Data/
│   ├── raw/
│   │   └── census.csv                  # Original census dataset
│   └── processed/
│       └── census_cleaned.csv          # Cleaned dataset ready for modeling
│
├── frontend/
│   ├── preview.html                    # Standalone client preview for browser testing
│   ├── README.md                       # Frontend integration notes
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css               # Styling, design tokens & responsive layout
│   │   └── js/
│   │       └── main.js                 # Frontend interactions & client logic
│   └── templates/
│       └── index.html                  # Jinja2 production template
│
├── ML_Notebook/
│   ├── MachineLearningTraining&Evaluation.ipynb  # Comprehensive model training & benchmarks
│   ├── model.pkl
│   └── preprocessor.pkl
│
├── Preprocessing/
│   ├── __init__.py
│   └── finding_donors_preprocessing.ipynb        # Data exploration, cleaning & feature prep
│
├── requirements.txt                    # Project Python dependencies
└── README.md                           # Project documentation
```

---

## API Reference

### Health Check

* **Endpoint:** `GET /health`
* **Response:**
  ```json
  {
    "status": "healthy",
    "model_loaded": true,
    "preprocessor_loaded": true
  }
  ```

### Prediction Endpoint

* **Endpoint:** `POST /predict`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "age": 39,
    "workclass": "State-gov",
    "education_level": "Bachelors",
    "education-num": 13.0,
    "marital-status": "Never-married",
    "occupation": "Adm-clerical",
    "relationship": "Not-in-family",
    "race": "White",
    "sex": "Male",
    "capital-gain": 2174.0,
    "capital-loss": 0.0,
    "hours-per-week": 40,
    "native-country": "United-States"
  }
  ```
* **Success Response (`200 OK`):**
  ```json
  {
    "prediction": 1,
    "income_category": ">50K",
    "message": "Prediction completed successfully."
  }
  ```

---

## Getting Started Locally

Follow these steps to set up and run CharityML on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/adamelhabian/Depi-Projects-AI.git
cd Depi-Projects-AI/ML/ML_P2
```

### 2. Create and Activate a Virtual Environment

* **Windows:**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Start the FastAPI development server with Uvicorn:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Access the Web Interface

Open your browser and navigate to:
```text
http://127.0.0.1:8000
```

---

## Acknowledgments

* **Digital Egypt Pioneers Initiative (DEPI)** - Ministry of Communications and Information Technology (MCIT), Egypt.
* **U.S. Census Bureau** for providing the Census Income dataset (Finding Donors).
