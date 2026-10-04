# House Price Prediction

A machine learning-based House Price Prediction system developed as a collaborative Machine Learning and Software Engineering project.

The project demonstrates an end-to-end machine learning workflow, starting from data analysis and preprocessing, followed by model development and optimization, and finally integrating the trained model into a web application with a Flask backend and frontend interface.

## Technologies & Tools

* Python
* Pandas
* NumPy
* Scikit-learn
* Flask
* HTML
* CSS
* Gunicorn
* Railway
* Git & GitHub
* Jupyter Notebook

## Project Features

* Exploratory Data Analysis (EDA)
* Data cleaning and preprocessing
* Feature engineering
* Feature scaling
* Machine learning model development
* Model evaluation and comparison
* Hyperparameter tuning
* Model optimization
* House price prediction
* Flask backend
* Web-based user interface
* Frontend-backend integration
* Production deployment

## Project Structure

```text
ML_P1/
│
├── data/
│   ├── .gitkeep
│   └── boston_housing_cleaned.csv
│
├── notebooks/
│   ├── NootbookbyAdam.ipynb
│   ├── visuals.py
│   └── Tspeeh_NoteBook/
│       ├── boston_housing.ipynb
│       ├── housing.csv
│       └── visuals.py
│
├── src/
│   │
│   ├── backend/
│   │   ├── app.py
│   │   ├── __init__.py
│   │   │
│   │   ├── models/
│   │   │   ├── model.pkl
│   │   │   └── scaler.pkl
│   │   │
│   │   └── services/
│   │       ├── prediction_service.py
│   │       └── __init__.py
│   │
│   ├── frontend/
│   │   ├── static/
│   │   │   └── css/
│   │   │       └── style.css
│   │   │
│   │   └── templates/
│   │       └── index.html
│   │
│   ├── ml/
│   │   ├── MLpart1/
│   │   │   ├── MLPhase1.ipynb
│   │   │   └── mlP1.txt
│   │   │
│   │   └── MLpart2/
│   │       ├── MLPhase2.ipynb
│   │       └── README.md
│   │
│   ├── preprocessing/
│   │   ├── preprocessing pipline.ipynb
│   │   └── scaler.joblib
│   │
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

## Installation

Follow these steps to install and run the project locally.

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Navigate to the Project Directory

```bash
cd ML_P1
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r src/requirements.txt
```

## How to Run

Run the Flask application from the project root:

```bash
python -m src.backend.app
```

The application will start locally and will usually be available at:

```text
http://127.0.0.1:5000
```

Open the URL in your browser to access the application.

## How It Works

The system follows an end-to-end machine learning workflow:

```text
Housing Dataset
       ↓
Data Analysis
       ↓
Data Preprocessing
       ↓
Model Training
       ↓
Model Evaluation
       ↓
Model Optimization
       ↓
Flask Backend
       ↓
Frontend
       ↓
House Price Prediction
```

## Team Contributions

### Maya — Data Analysis & Preprocessing

Responsible for preparing the dataset and making it ready for machine learning.

* Exploratory Data Analysis
* Data visualization
* Missing value analysis
* Duplicate analysis
* Outlier analysis
* Data cleaning
* Feature analysis
* Data preprocessing
* Feature scaling
* Preparing the ML-ready dataset

### Tspeeh — Machine Learning Preparation & Evaluation

Responsible for preparing the machine learning workflow and evaluation process.

* Train/test split
* Machine learning preparation
* Model evaluation setup
* Learning curves
* Bias-variance analysis
* Model performance analysis
* Supporting the model comparison process

### Youssef — Machine Learning & Optimization

Responsible for developing and optimizing the machine learning models.

* Model development
* Model training
* Model comparison
* Hyperparameter tuning
* Model optimization
* Performance improvement
* Final model selection
* Final model evaluation
* Preparing the final model for integration

### Adam — Backend Development & Deployment

Responsible for integrating the machine learning model into the web application and deploying the system.

* Flask backend development
* Machine learning model integration
* Loading the trained model
* Loading preprocessing artifacts
* Prediction service development
* Handling user input
* Connecting the frontend with the backend
* Returning house price predictions
* Backend testing
* Gunicorn configuration
* Railway deployment

### Mina — Frontend Development

Responsible for developing the user interface and connecting it with the backend.

* Frontend development
* User input form
* HTML and CSS implementation
* User interface design
* Sending input data to the backend
* Receiving prediction results
* Displaying predicted house prices
* Frontend-backend integration

## Deployment

The application is prepared for production deployment using Gunicorn and Railway.

```text
Flask
   ↓
Gunicorn
   ↓
Railway
   ↓
Public Web Application
```

## Project Status

**Status:** Deployed / In Development

## Future Improvements

* Improve prediction accuracy
* Add additional machine learning models
* Improve frontend design
* Add input validation
* Add automated testing
* Add database integration
* Add user authentication
* Improve monitoring and logging

## Contributors

This project was developed collaboratively by a team of five developers as part of the DEPI Machine Learning project.

| Contributor               | Contribution                              |
| ------------------------- | ----------------------------------------- |
| Adam Elhabian             | Backend Development & Deployment          |
| Mina Safwat               | Frontend Development                      |
| Maya Amged                | Data Analysis & Preprocessing             |
| Youssef Mohamed Abdelkrem | Machine Learning & Model Optimization     |
| Tasbeeh Hassan            | Machine Learning Preparation & Evaluation |
