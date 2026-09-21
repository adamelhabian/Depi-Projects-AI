# Ford GoBike Data Engineering & Analytics Platform

An end-to-end Data Engineering and Analytics project built using the **Ford GoBike bike-sharing dataset**.

The project processes raw data through an ETL pipeline, stores it in a PostgreSQL Data Warehouse using **Supabase**, and provides analytics through an interactive **Streamlit dashboard**.

## Project Architecture

```text
Raw CSV
   ↓
Extract
   ↓
Bronze Layer
   ↓
Transform
   ↓
Silver Layer
   ↓
Data Warehouse
   ↓
Gold Layer
   ↓
Dashboard
```

## Data Layers

### Bronze

Stores the original raw data with minimal changes.

```text
bronze.trips
```

### Silver

Contains cleaned and transformed data.

Main transformations include:

- Data type handling
- Missing-value handling
- Date and time extraction
- Age calculation
- Feature creation
- Data validation

```text
silver.trips
```

### Data Warehouse

The warehouse uses a **Star Schema**.

**Fact Table**

```text
warehouse.fact_trip
```

**Dimension Tables**

```text
warehouse.dim_date
warehouse.dim_time
warehouse.dim_station
warehouse.dim_user
```

### Gold

Contains analytics-ready SQL views used by the dashboard.

```text
gold.*
```

## ETL Pipeline

The pipeline is managed through:

```text
pipeline/pipeline.py
```

Workflow:

```text
Extract
   ↓
Load Bronze
   ↓
Transform
   ↓
Load Silver
   ↓
Build Dimensions
   ↓
Build Fact Table
   ↓
Create Gold Views
   ↓
Validate
```

## Project Structure

```text
ford_gobike_analysis/
│
├── dashboard/
│   ├── master-dashboard/
│   │   ├── app.py
│   │   ├── callbacks/
│   │   │   ├── export_callbacks.py
│   │   │   ├── global_filter_callbacks.py
│   │   │   ├── global_filter_sync.py
│   │   │   ├── overview_callbacks.py
│   │   │   └── routing.py
│   │   ├── components/
│   │   │   ├── footer.py
│   │   │   ├── global_filter_bar.py
│   │   │   ├── key_insights.py
│   │   │   ├── kpi_banner.py
│   │   │   └── navbar.py
│   │   ├── assets/
│   │   │   └── master_style.css
│   │   ├── README.md
│   │   ├── Procfile
│   │   └── requirements.txt
│   │
│   ├── station-trip-analysis/
│   │   ├── assets/
│   │   │   └── style.css
│   │   ├── README.md
│   │   └── requirements.txt
│   │
│   ├── time-user-analysis/
│   │   ├── assets/
│   │   │   └── style.css
│   │   ├── README.md
│   │   └── requirements.txt
│   │
│   ├── database.py
│   ├── Procfile
│   ├── .gitignore
│   └── requirements.txt
│
├── data/
│   └── bronze/
│       └── raw source data
│
├── eda/
│   └── notebooks/
│       ├── EDA_adam.ipynb
│       ├── EDA_youssef.ipynb
│       ├── EDA_Taspeeh.ipynb
│       └── EDA_Tspeeh_Time_User.ipynb
│
├── preprocessing/
│   ├── preprocessing.ipynb
│   └── cleaned_fordgobike_master.csv
│
├── Gold_DF/
│   ├── station_metrics/
│   │   ├── station_metrics.ipynb
│   │   └── Station_Metrics.csv
│   │
│   ├── top_destination/
│   │   ├── top_destination..ipynb
│   │   └── Top_Destination.csv
│   │
│   └── top_routes/
│       ├── Top_Routes.ipynb
│       └── Top_Routes.csv
│
├── database/
│   ├── bronze/
│   │   └── create_tables.sql
│   │
│   ├── silver/
│   │   └── create_tables.sql
│   │
│   ├── gold/
│   │   └── views.sql
│   │
│   └── warehouse/
│       ├── dimensions.sql
│       └── facts.sql
│
├── pipeline/
│
├── ExploratoryDataAnalysis_Phase/
│   ├── EDA_by_Tspeeh/
│   └── UI/
│       └── UI.ipynb
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Dashboard

The dashboard is built with **Streamlit** and **Plotly**.

It uses the Gold layer to provide analytics such as:

- Total trips
- Active stations
- Average trip duration
- Subscriber ratio
- Peak hours
- Station flow
- Rider demographics
- Trip patterns
- Interactive filtering

## Database

The project uses **PostgreSQL through Supabase**.

```text
Python ETL Pipeline
        ↓
SQLAlchemy
        ↓
Supabase PostgreSQL
        ↓
┌─────────┬─────────┬────────────┬────────┐
│ Bronze  │ Silver  │ Warehouse  │  Gold  │
└─────────┴─────────┴────────────┴────────┘
```

The database connection is stored in an environment variable:

```env
DATABASE_URL=your_supabase_database_url
```

Database credentials are not stored in the repository.

## Technologies

- Python
- Pandas
- SQLAlchemy
- PostgreSQL
- Supabase
- SQL
- Streamlit
- Plotly
- Jupyter Notebook
- Git & GitHub

## How to Run

### 1. Clone the repository

```bash
git clone <repository-url>
cd ford_gobike_analysis
```

### 2. Create a virtual environment

```bash
python -m venv .venv_DA
```

Activate it:

```bash
.venv_DA\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database

Create a `.env` file:

```env
DATABASE_URL=your_supabase_database_url
```

### 5. Run the ETL pipeline

```bash
python pipeline/pipeline.py
```

### 6. Run the dashboard

```bash
streamlit run dashboard/app.py
```

## Team Workflow

```text
Data Source
    ↓
Data Engineering
    ↓
Data Warehouse
    ↓
Gold Analytics
    ↓
Dashboard
```

The centralized Supabase database allows the team to work with the same data source instead of using separate local databases.

## Key Outcome

The project demonstrates a complete Data Engineering workflow:

**Raw Data → ETL → Data Warehouse → Gold Analytics → Interactive Dashboard**

It combines data cleaning, ETL, dimensional modeling, cloud PostgreSQL, SQL analytics, and interactive visualization in one end-to-end platform.

## Contributors

This project was developed collaboratively by a team of five members as part of the **DEPI Data Analysis & Engineering project**.

| Contributor                   |
| ----------------------------- |
| **Adam Elhabian**             |
| **Mina Safwat**               |
| **Maya Amged**                |
| **Youssef Mohamed Abdelkrem** |
| **Tasbeeh Hassan**            |
