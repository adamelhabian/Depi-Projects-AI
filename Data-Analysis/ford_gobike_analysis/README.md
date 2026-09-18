# Ford GoBike Data Engineering & Analytics

An end-to-end **Data Engineering and Analytics** project built using the Ford GoBike dataset.

The project transforms raw trip data into a structured **PostgreSQL Data Warehouse** using a Bronze → Silver → Warehouse → Gold architecture, then provides dashboard-ready data for visualization and analysis.

---

## Architecture

```text
Raw CSV Files
      ↓
   Bronze
      ↓
   Silver
      ↓
 Data Warehouse
      ↓
    Gold
      ↓
  Dashboard
```

The database is hosted on **Supabase PostgreSQL**, providing a shared database for the ETL pipeline and dashboard.

---

## Project Structure

```text
ford_gobike_analysis/
│
├── config/
│   └── database.py          # Database connection & configuration
│
├── dashboard/
│   └── app.py               # Streamlit dashboard
│
├── data/
│   ├── raw/                 # Original CSV files
│   └── cleaned/             # Cleaned data
│
├── database/
│   ├── 01_bronze.sql       # Bronze layer
│   ├── 02_silver.sql       # Silver layer
│   ├── 03_warehouse.sql    # Data warehouse
│   └── 04_gold.sql         # Gold views
│
├── docs/                    # Documentation & architecture
│
├── notebooks/               # Exploratory data analysis
│   ├── EDA_adam.ipynb
│   ├── EDA_Taspeeh.ipynb
│   └── EDA_youssef.ipynb
│
├── pipeline/
│   ├── __init__.py
│   ├── extract.py           # Data extraction
│   ├── transform.py         # Data cleaning & transformation
│   ├── load.py              # Database loading
│   └── pipeline.py          # ETL orchestrator
│
├── .env                     # Environment variables
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Data Layers

### Bronze

Stores the raw data with minimal changes.

```text
bronze.trips
```

### Silver

Contains cleaned and transformed data.

Main transformations include:

- Timestamp reconstruction
- Data type standardization
- Invalid data removal
- `duration_min`
- `member_age`
- `age_group`

```text
silver.trips
```

### Data Warehouse

Uses a **Star Schema**:

```text
                 dim_date
                    │
dim_station ── fact_trip ── dim_user
                    │
                 dim_time
```

The fact table stores trip-level measurements, while dimensions provide descriptive information.

### Gold

Provides a dashboard-ready view combining the required warehouse information.

```text
gold.trip_analytics
```

---

## ETL Pipeline

Run the complete pipeline with:

```bash
python pipeline/pipeline.py
```

The pipeline performs:

```text
Extract
   ↓
Initialize Database
   ↓
Load Bronze
   ↓
Transform → Silver
   ↓
Load Warehouse
   ↓
Create Gold View
   ↓
Validate
```

---

## Dashboard

The dashboard connects to the **Gold layer** instead of directly querying multiple warehouse tables.

This allows the dashboard to focus on visualization and insights while the ETL pipeline handles data preparation.

Possible analysis includes:

- Trip volume
- Trip duration
- User behavior
- Time patterns
- Popular stations
- Gender and age analysis
- Geographic analysis

---

## Database

The project uses **Supabase PostgreSQL** as the shared database.

```text
ETL Pipeline
     ↓
Supabase PostgreSQL
     ↓
Gold View
     ↓
Streamlit Dashboard
```

Database credentials are stored in `.env` and should never be committed to Git.

---

## Technologies

- Python
- Pandas
- PostgreSQL
- Supabase
- SQLAlchemy
- Streamlit
- Plotly
- Jupyter Notebook
- Git & GitHub

---

## Project Goal

The goal is to build a complete data pipeline that transforms raw Ford GoBike trip data into reliable, structured, and dashboard-ready information for analytics and visualization.
