# Hospital Management System

A Python-based Hospital Management System developed as a collaborative Object-Oriented Programming project.

The project simulates the core entities and relationships within a hospital while applying fundamental Object-Oriented Programming and Software Engineering concepts.

## Technologies & Tools

- Python
- Streamlit
- Git & GitHub
- UML
- diagrams.net (draw.io)

## OOP Concepts

- Classes and Objects
- Encapsulation
- Inheritance
- Polymorphism
- Abstraction
- Composition
- Association

## Project Structure

```text
hospital-management-system/
│
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── person.py
│   │   ├── patient.py
│   │   ├── staff.py
│   │   ├── doctor.py
│   │   ├── department.py
│   │   ├── hospital.py
│   │   └── appointment.py
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── ui_appointment.py
│   │   ├── ui_dashboard.py
│   │   ├── ui_medical_operations.py
│   │   ├── ui_patient.py
│   │   ├── ui_reports.py
│   │   └── ui_staffs_and_doctors.py
│   │
│   ├── utility/
│   │   ├── __init__.py
│   │   └── helpers.py
│   │
│   ├── main.py
│   └── ui_main.py
│
├── diagrams/
│   └── class-diagram.png
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

Follow these steps to install and run the project locally.

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Navigate to the Project Directory

```bash
cd hospital-management-system
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

Install all required Python packages using:

```bash
pip install -r requirements.txt
```

## How to Run

After activating the virtual environment and installing the dependencies, run the Streamlit application:

```bash
streamlit run src/ui_main.py
```

Streamlit will start the application and provide a local URL in the terminal.

Usually, the application will be available at:

```text
http://localhost:8501
```

Open the URL in your web browser to access the Hospital Management System.

## How to Use

After launching the application, you can navigate through the different sections of the system, including:

- Dashboard
- Patients
- Staff and Doctors
- Appointments
- Medical Operations
- Reports

The application provides a graphical interface for managing and interacting with the hospital's main entities.

## Project Status

**Status:** In Development

## Future Improvements

- Database integration
- Additional hospital management features
- Improved UI and user experience
- Automated testing
- Authentication and user roles
- Data persistence

## Contributors

This project is developed collaboratively by a team of five developers as part of the DEPI Python/OOP project.

| Contributor               |
| ------------------------- |
| Adam Elhabian             |
| Mina Safwat               |
| Maya Amged                |
| Youssef Mohamed Abdelkrem |
| Tasbeeh Hassan            |
