# Educational Management System — EduWise

## 1. About the System

An intelligent educational management system that helps teachers manage students, groups, classes, exams, payments, and parent communication in one place.

The system integrates Machine Learning, AI, and automation to improve educational management and support data-driven decisions.

## EduFlow AI frontend

[Sign in to EduFlow AI](https://eduflow-ai-brand.vercel.app/) to access the shared workspace. The [sample workspace](https://eduflow-ai-brand.vercel.app/?mode=demo#overview) runs with sample data in the browser.

The [AI automation module documentation](src/ai_automation/README.md) and [n8n automation runbook](src/ai_automation/n8n_ai_automation_plan.md) explain how to configure and verify Telegram guardian alerts and Gemini-assisted homework grading.

## 2. System Users

The system is designed for two main users:

### Teacher

- Manage students and study groups.
- Organize class schedules and sessions.
- Track attendance and academic performance.
- Create exams and review student results.
- Monitor payments, expenses, and financial reports.
- Use AI tools and ML insights to support decisions.

### Secretary

- Manage student registration and information.
- Organize groups and student records.
- Record attendance and payments.
- Prepare messages and communicate with parents.
- Assist the teacher with daily administrative tasks.

## 3. System Features

### 3.1 Student Management

- Add, update, search, and manage student profiles.
- Store student and parent contact information.
- View student groups, attendance, exams, and payments.

### 3.2 Group & Schedule Management

- Create and manage study groups.
- Enroll students in groups.
- Organize class schedules and sessions.

### 3.3 Attendance Management

- Record student attendance for each session.
- Track absences and late attendance.
- Identify students with repeated absences.

### 3.4 Exams & Results

- Create exams and assign them to groups.
- Record and manage student marks.
- Track student progress and academic performance.

### 3.5 Financial Management

- Record student payments and outstanding fees.
- Track expenses.
- Generate basic financial summaries and reports.

### 3.6 Parent Communication

- Prepare messages for parents.
- Send absence notifications and payment reminders.
- Select individual students or entire groups.

### 3.7 Machine Learning Features

- **Student Segmentation:** Group students based on academic performance and attendance patterns.
- **Academic Risk Prediction:** Identify students who may need additional academic support.
- **Dropout Risk Prediction:** Identify students who may be at risk of leaving.
- **Revenue Forecasting:** Estimate future revenue using historical financial data.

### 3.8 AI Features

- **AI Exam Generation:** Generate exam questions from teacher-uploaded educational PDFs.
- **RAG (Retrieval-Augmented Generation):** Retrieve relevant information from uploaded educational materials to generate context-based responses.
- **AI Chatbot:** Answer students' and parents' questions using approved system information, such as schedules and lesson details.
- **Telegram AI Automation:** Integrate AI-powered Telegram bots to automate notifications, answer queries, and support communication and daily educational workflows.

## 4. Project Structure

```text
EduWise/
│
├── data/
│   ├── raw/                       # Original datasets
│   ├── processed/                 # Cleaned datasets
│   └── .gitkeep
│
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py             # Application configuration
│   │
│   ├── backend/
│   │   ├── routes/                 # API endpoints
│   │   ├── schemas/                # Request/response validation
│   │   ├── services/               # Business logic
│   │   ├── database/               # Database connection and queries
│   │   └── main.py                 # FastAPI entry point
│   │
│   ├── machine_learning/
│   │   ├── preprocessing/          # Data cleaning and preparation
│   │   ├── models/                 # Model definitions and saved models
│   │   ├── training/               # Model training scripts
│   │   └── evaluation/             # Metrics and model evaluation
│   │
│   ├── rag/
│   │   ├── ingestion/              # Document loading and chunking
│   │   ├── retrieval/               # Document retrieval
│   │   ├── generation/              # LLM response generation
│   │   └── __init__.py
│   │
│   ├── ai_automation/
│   │   ├── workflows/               # AI automation workflows
│   │   └── integrations/            # External service integrations
│   │
│   └── shared/
│       ├── helpers/                 # Reusable helper functions
│       └── utils/                   # General-purpose utilities
│
├── frontend/                        # Frontend application
│
├── tests/
│   ├── test_backend.py
│   ├── test_ml.py
│   └── test_rag.py
│
├── .env                             # Local secrets (not committed)
├── .env.example                     # Environment variable template
├── .gitignore
├── README.md
└── requirements.txt
```

### Directory Responsibilities

| Directory               | Responsibility                                                               |
| ----------------------- | ---------------------------------------------------------------------------- |
| `data/raw/`             | Store original datasets.                                                     |
| `data/processed/`       | Store cleaned and processed datasets.                                        |
| `src/backend/`          | Handle API endpoints, business logic, validation, and database operations.   |
| `src/machine_learning/` | Handle data preprocessing, model training, prediction, and evaluation ([Machine Learning README](src/machine_learning/README.md)). |
| `src/rag/`              | Handle document ingestion, retrieval, and context-based response generation. |
| `src/ai_automation/`    | Handle AI-powered automation workflows and integrations ([AI Automation README](src/ai_automation/README.md)). |
| `src/shared/utils/`     | Store reusable helper functions shared across components.                    |
| `frontend/`             | Contain the user interface and frontend application.                         |
| `tests/`                | Contain tests for backend, ML, and RAG components.                           |

_Note: This structure represents the planned architecture. Directories and files can be added as implementation progresses._

## 5. Development Team & Responsibilities

The project is divided into independent development components.

### Frontend Development

- Build the user interface and system pages.
- Implement reusable components.
- Connect the frontend with backend APIs.

### Backend Development

- Develop APIs and business logic.
- Design and manage the database.
- Handle authentication, authorization, and system operations.
- Integrate with ML and AI services.

### Machine Learning Development

- Prepare and process datasets.
- Perform feature engineering.
- Train and evaluate ML models.
- Build prediction pipelines and integrate model outputs.

### AI & Automation Development

- Implement RAG and document processing.
- Develop the AI chatbot.
- Build AI exam generation.
- Develop Telegram bots and automation workflows.

## 6. Development Approach

- Each component will be developed independently.
- Teams will work in parallel using agreed API contracts and data formats.
- Components will be tested independently before integration.
- Agile methodology will be used to organize tasks, track progress, and deliver features incrementally.

## 7. Project Goal

The main goal is to reduce teachers' administrative workload, organize educational operations, monitor student progress, and provide useful insights through data analysis, Machine Learning, AI, and automation.

> AI-generated content and predictions are decision-support tools. Teachers remain responsible for reviewing generated exams and making final educational decisions.

## Academic risk and parent alerts

Run these commands from `Graduation Project/EduWise` using Python 3.13. The supplied CSVs, model, and report are ready to use. To reproduce them on Windows:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m data.generate_academic_data
python -m src.machine_learning.training.train_academic_risk
python -m src.machine_learning.evaluation.evaluate_academic_risk
$pytestBase = Join-Path (Resolve-Path .venv) ('pytest-' + [guid]::NewGuid())
python -m pytest -q --basetemp $pytestBase
```

The seed-42 generator produces 3,000 fictional student snapshots. The binary label represents a simulated later assessment below 57/100. `data/processed/` contains validated, stratified train/test splits. Each training fold fits its own median imputer, scaler, and group encoder. Seven configurations across three classifier families compete on out-of-fold positive-class F1, with recall breaking ties. The holdout scores, selected threshold, package versions, and confusion matrix are in [metrics.json](src/machine_learning/evaluation/metrics.json). These scores measure performance on synthetic students. Validate against local outcomes before relying on them for educational decisions.

### Backend integration

Create one service per worker and load only a trusted, project-controlled joblib file. The load checks the recorded Python major/minor and model-library versions. Map `InvalidStudentData` to an input error and `ModelUnavailableError` to a service availability error.

```python
from src.backend.services.academic_risk_service import AcademicRiskService

service = AcademicRiskService()
result = service.predict({
    "student_id": "EG-00001", "group_id": "G-01",
    "attendance_rate": 0.55, "homework_completion_rate": 0.45,
    "average_quiz_score": 48, "midterm_score": 50, "participation_score": 52,
    "missed_sessions_count": 3,
})
```

Rates are fractions, scores are 0–100, and the optional ordered quiz slots are `quiz_oldest`, `quiz_middle`, and `quiz_latest`. Omit unknown measurements or pass JSON null. Supply at least one observed measurement. Student identity, name, and fee delay do not enter the model. The absence count covers up to eight recent eligible sessions for this student and group. For raw attendance use `count_absences` with eligible sessions in chronological order, retaining excused and unrecorded slots in the window. Only confirmed unexcused absences increment the count.

### Explainability (TreeSHAP) and What-If Simulation

The service provides native TreeSHAP feature attributions and counterfactual simulation:

```python
# Explain model prediction
explanation = service.explain(student_data)
# explanation["top_risk_factors"]: list of factors increasing risk
# explanation["top_protective_factors"]: list of protective factors
# explanation["recommended_actions"]: pedagogical advice in Arabic & English

# Simulate hypothetical improvement
simulation = service.simulate_what_if(student_data, improvements={
    "attendance_rate": 0.90,
    "quiz_latest": 80,
    "missed_sessions_count": 0,
})
# simulation["risk_reduction"]: drop in risk probability
# simulation["rescued_from_risk"]: true if student leaves danger zone
```

### Automation Architecture Note (n8n Integration)

Workflows for parent communication, absence alerts, and automated follow-ups are decoupled from the core ML model. They are orchestrated via an external **n8n** automation workflow triggered by API webhooks upon student evaluation events. See the [AI automation module documentation](src/ai_automation/README.md) for endpoint contracts, SQLite audit tables, and Telegram bot commands.

