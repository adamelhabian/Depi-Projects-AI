# Ford GoBike Analytics — Time & User Analysis (Member 4)

> **Collaborative Data Analytics Project | DEPI Project**  
> Modern, focused behavioral analytics dashboard exploring diurnal commuting rhythms, weekly usage intensity, and rider demographic segmentation built with **Dash**, **Plotly**, and **Tailwind CSS**.

---

## 👥 Member 4 Scope & Responsibilities

| Role | Scope |
|---|---|
| **Member 4: Behavioral & Temporal Analytics** | **Time-Series Trends, Peak Commuting Rhythms, Rider Demographics, and User Segmentation** |

---

## 🚀 Dashboard Architecture & Features

This dashboard is designed as a clean, self-contained analytical view with zero clutter and no extraneous navigation wrappers:

### 1. Headline KPI Cards
* **Total Trips**: Live trip count matching active filter parameters.
* **Subscriber Ratio**: Percentage of trips completed by annual pass commuter subscribers.
* **Peak Commute Window**: Hour of highest network volume (e.g. 8:00 AM / 5:00 PM).
* **Average Ride Duration**: Mean journey duration in minutes.

### 2. Five Core Visualizations (Strictly Focused Scope)
* **Hourly Trip Demand Profile**: Diurnal volume distribution revealing the twin commuter rush peaks (8–9 AM & 5–6 PM).
* **Day-of-Week Riding Volume**: Crystal-clear volume comparison across Monday through Sunday contrasting high weekday commuter demand (~25K–34K/day) with the ~50% drop on weekends.
* **Rider Membership Split**: Horizontal comparative breakdown of Subscribers vs. Casual Customers.
* **Hourly Pattern by User Type**: Normalized comparative trends showing how Subscribers drive commuter peaks while Customers ride midday.
* **Rider Age Cohort Distribution**: Demographic volume distributed across defined age brackets (18–25, 26–35, 36–50, 51–65, 66–80).

### 3. Reactive Filter Slicers
* **Rider Membership Filter**: Slices data by `All Riders`, `Subscribers`, or `Customers`.
* **Temporal Day Classification**: Slices data by `All Days`, `Weekdays Only`, or `Weekends Only`.

### 4. Direct Cloud Data Layer (Supabase Exclusively)
* **Direct Cloud Ingestion**: Queries `gold.trip_analytics` directly from Supabase PostgreSQL cloud database.
* **100% In-Memory Processing**: Zero reliance on local CSV files.

---

## 📁 Repository Structure

```text
time-user-analysis/
├── app.py                      # Dash application entry point (Default Port: 8051)
├── config.py                   # Central component IDs, palette, and chart constants
├── data_loader.py              # Supabase cloud loader with memory caching
├── layout.py                   # Master clean layout (Header + 4 KPIs + Filter Bar + 5 Charts + Footer)
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation & integration guide
│
├── callbacks/
│   ├── __init__.py
│   └── dashboard_callbacks.py  # Reactive controller for filters, KPIs, and 5 charts
│
├── components/
│   ├── __init__.py
│   ├── chart_card.py           # Reusable Tailwind chart container
│   └── filter_panel.py         # Slicer controls for membership and day classification
│
├── charts/
│   ├── __init__.py
│   ├── time_analysis.py        # Hourly demand and weekly heatmap visualizations
│   └── user_analysis.py        # Membership, behavioral hourly, and age cohort charts
│
├── tests/
│   └── test_time_user_dashboard.py # Automated verification suite
│
└── utils/
    ├── __init__.py
    ├── data_processing.py      # KPI computations and reactive dataset filtering
    └── theme.py                # Color palettes and Plotly styling
```

---

## 🛠️ Quickstart & Local Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Ensure `.env` contains your Supabase PostgreSQL credentials:
```env
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<dbname>
```

### 3. Run the Dashboard
```bash
python app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:8051`**
