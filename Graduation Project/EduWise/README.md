# Educational Management System — EduWise

## 1. About the System

An intelligent educational management system that helps teachers manage students, groups, classes, exams, payments, and parent communication in one place.

The system integrates Machine Learning, AI, and automation to improve educational management and support data-driven decisions.

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
│   ├── raw/
│   ├── processed/
│   └── .gitkeep
│
├── src/
│   ├── backend/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database/
│   │   └── main.py
│   │
│   ├── machine_learning/
│   │   ├── preprocessing/
│   │   ├── models/
│   │   ├── evaluation/
│   │   └── training/
│   │
│   ├── rag/
│   │   ├── ingestion/
│   │   ├── retrieval/
│   │   ├── generation/
│   │   └── __init__.py
│   │
│   ├── ai_automation/
│   │
│   └── shared/
│       └── utils/
│
├── frontend/
│
├── tests/
│   ├── test_backend.py
│   ├── test_ml.py
│   └── test_rag.py
│
├── .env.example
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
| `src/machine_learning/` | Handle data preprocessing, model training, prediction, and evaluation.       |
| `src/rag/`              | Handle document ingestion, retrieval, and context-based response generation. |
| `src/ai_automation/`    | Handle AI-powered automation workflows and integrations.                     |
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
