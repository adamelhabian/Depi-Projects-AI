# Ford GoBike Analytics — Time & User Analysis (Member 4)

> **Collaborative Data Analytics Project | DEPI Project**  
> Interactive temporal and demographic behavioral analytics, peak commuting pattern discovery, rider segmentation, and operational scheduling built with **Dash**, **Plotly**, and **Tailwind CSS**.

---

## 👥 Team Responsibilities

| Role | Member | Scope |
|---|---|---|
| Member 1 | Database Engineering | PostgreSQL Database Architecture, Views & SQL Pipeline |
| Member 2 | Data Engineering | Data Cleaning, Pipeline Processing & Master Datasets |
| Member 3 | BI & KPI Design | High-Level KPI Tiles, Global Filters & Executive Metrics |
| **Member 4** | **Time & User Analysis** | **Time-Series Trends, Peak Hours, User Demographics & Prescriptive Scheduling** |
| Member 5 | Station & Trip Analysis | Network Traffic Hubs, Flow Corridors, Rebalancing & Station Deep Dives |

---

## 🚀 Key Features & Capabilities

### 1. Temporal Dynamics & Commute Patterns
* **Hourly Trip Distribution**: Visualizes diurnal rhythms, distinguishing morning rush (8–9 AM) and evening rush (5–6 PM).
* **Day-of-Week & Seasonal Trends**: Contrast weekday commuter spikes against weekend leisure profiles.
* **Peak Utilization Heatmaps**: Interactive cross-tabulation of day-of-week vs. hour-of-day.

### 2. User Segmentation & Demographics
* **Subscriber vs. Customer Behavior**: Comparative analysis of trip frequency, duration distributions, and usage schedules.
* **Rider Demographics**: Age cohort breakdowns, gender distributions, and bike-share-for-all program adoption.
* **Duration & Speed Profiling**: Segmentation of trips by ride length, speed estimates, and loop journeys.

### 3. Prescriptive Scheduling & Resource Allocation
* **Peak Hour Resource Guidance**: Data-driven recommendations for bike availability during commuter rush hours.
* **Weekend Leisure Readiness**: Operational guidelines for high-demand recreational docks during weekends.

### 4. Interactive Sidebar & Global Navigation
* **Dedicated Navigation Sidebar**: Smooth collapsible sidebar with section links, filter controls, and active view highlights.
* **Configurable Metric Slicers**: Dynamic date range, user type, and demographic filters.

### 5. High-Performance Data Layer
* **Direct Cloud Ingestion**: Queries `gold.trip_analytics` directly from Supabase PostgreSQL database.
* **Resilient Offline Fallback**: Automatically switches to local CSV if credentials or network connectivity are unavailable.

---

## 📁 Repository Structure

```text
time-user-analysis/
├── app.py                      # Dash application entry point (Default Port: 8051)
├── config.py                   # Theme colors, chart configurations, and component IDs
├── data_loader.py              # Supabase cloud loader with caching & CSV fallback
├── layout.py                   # Master layout (Sidebar + Header + Time Analysis + User Analysis)
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation & integration guide
│
├── callbacks/
│   ├── __init__.py
│   └── dashboard_callbacks.py  # Reactive callbacks for filters, charts, and interactions
│
├── components/
│   ├── __init__.py
│   ├── chart_card.py           # Standard card wrapper
│   ├── filter_panel.py         # Global filter bar
│   ├── icons.py                # Standalone SVG icon library
│   └── sidebar.py              # Collapsible navigation sidebar
│
├── charts/
│   ├── __init__.py
│   ├── time_analysis.py        # Hourly, daily, weekly, and heatmap charts
│   └── user_analysis.py        # Subscriber vs Customer, demographic breakdowns
│
└── utils/
    ├── __init__.py
    ├── data_processing.py      # Aggregations, filtering, and metric calculations
    └── theme.py                # Color palettes, fonts, and styling constants
```

---

## 🛠️ Quickstart & Local Setup

### 1. Environment & Dependencies
Ensure Python 3.10+ is installed. Install required packages:
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
python app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:8051`**

*(Note: Default port is set to `8051` so both Member 4 and Member 5 dashboards can run concurrently without port conflict).*
