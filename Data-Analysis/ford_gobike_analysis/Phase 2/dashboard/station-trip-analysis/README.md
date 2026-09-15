# Ford GoBike Analytics — Station & Trip Analysis (Member 5)

> **Collaborative 5-Member Data Analytics Project | DEPI Final Project**  
> Comprehensive geospatial network analysis, corridor trip patterns, spatial rebalancing dispatch, and station drill-downs.

---

## 👥 Team Responsibilities

| Role | Member | Scope |
|---|---|---|
| Member 1 | Database Engineering | PostgreSQL Database Architecture & Queries |
| Member 2 | Data Engineering | Data Processing, Cleaning & Master Dataset Preparation |
| Member 3 | BI & KPI Design | Dashboard Filters, Global KPIs & Key Insights |
| Member 4 | Behavioral Analytics | Time Analysis & User Demographics (Age/Gender) |
| **Member 5** | **Station & Trip Analysis** | **Network Traffic Hubs, Route Corridors, Rebalancing & Station Deep Dives** |

---

## 🚀 Key Features & Advanced Capabilities (7 Enhancements)

1. **Station Traffic & Flow Corridor Map (Geospatial Network)**
   * **Node Sizing & Coloring**: Size encodes total traffic ($\text{Departures} + \text{Arrivals}$); color encodes Net Flow (Green = Surplus, Red = Deficit).
   * **Flow Corridor Lines**: Renders transit line arcs between top origin–destination hubs directly on the map.
   * **Click-to-Inspect**: Clicking any station node immediately triggers the deep-dive inspector.

2. **Metro Region Cluster Selector (Auto-centering & Zoom)**
   * Filters the entire dashboard seamlessly across three discrete Bay Area metropolitan clusters:
     - **All Bay Area** (329 stations)
     - **San Francisco** (156 stations)
     - **East Bay (Oakland / Berkeley)** (127 stations)
     - **San Jose** (46 stations)
   * Automatically re-centers and zooms the viewport to the selected metropolitan area.

3. **Interactive Station Profile Inspector (`clickData` Drill-Down)**
   * Click any station on the geospatial map or the Top Stations ranking chart to reveal:
     - Real-time KPI stat badges: Total Trips, Departures, Arrivals, Net Flow, Imbalance Ratio %, and Round-Trip %.
     - **Top 5 Destinations**: Where riders travel to after unlocking bikes at this station.
     - **Top 5 Origins**: Where incoming riders originate from when returning bikes here.

4. **Prescriptive Smart Fleet Rebalancing (Haversine Spatial Matching)**
   * Automated rebalancing engine matching high-deficit stations with nearby high-surplus neighbors within the same metropolitan cluster.
   * Computes great-circle Haversine distances in kilometers/meters and calculates optimal bike transfer quantities ($\text{Net Flow} // 2$).

5. **Leisure & Tourism Hotspots (Round-Trip Journey Analysis)**
   * Identifies recreational loops ($\text{start\_station} == \text{end\_station}$) indicative of tourist activity.
   * Highlights landmarks like *Fell St at Stanyan St* (Golden Gate Park) with elevated loop percentages (~17.4%).

6. **Normalized Station Flow Imbalance Ratio %**
   $$\text{Imbalance Ratio} = \left(\frac{\text{Net Flow}}{\text{Total Traffic}}\right) \times 100$$
   * Normalizes inbound/outbound pressure relative to station scale, allowing fair comparison between giant hubs and smaller peripheral docks.

7. **One-Click CSV Data Export**
   * Built-in `dcc.Download` button generating on-the-fly CSV downloads of the active filtered station metrics dataset.

---

## 📐 Mathematical Definitions & Metric Rules

$$\text{Total Traffic} = \text{Departures} + \text{Arrivals}$$

$$\text{Net Flow} = \text{Arrivals} - \text{Departures}$$

* **Canonical Station Identity**: Stations are grouped strictly by canonical `station_name`. Coordinates are aggregated as station attributes (median GPS position) rather than grouping keys, preventing station duplication caused by GPS noise.
* **Coordinate Independence**: Stations with missing or unrecorded GPS coordinates are **not** excluded from ranking or imbalance analyses; they are gracefully filtered only from the geospatial map.
* **Strict Imbalance Classification**:
  * $\text{Deficit (Outbound Pressure)} \implies \text{Net Flow} < 0$
  * $\text{Surplus (Inbound Pressure)} \implies \text{Net Flow} > 0$
  * Neutral stations ($\text{Net Flow} = 0$) are never fabricated into either category.
* **No Fake Routes**: Routes are only generated when both origin and destination stations are non-null and valid.

---

## 📁 Clean Repository Structure

```text
member5/
├── app.py                      # Standalone entry point & WSGI server instance
├── config.py                   # Central theme colors, region presets, and component IDs
├── data_loader.py              # Single-load cached data loader with schema validation
├── layout.py                   # Modular layout hierarchy (Map -> Rankings -> Hotspots -> Inspector)
├── requirements.txt            # Pinned, production-ready dependencies
├── .gitignore                  # Git ignore rules (cache, venv, large CSV files)
├── README.md                   # Complete module documentation and team contract
│
├── callbacks/
│   ├── __init__.py
│   └── dashboard_callbacks.py  # Reactive controller for filters, inspector, and CSV export
│
├── components/
│   ├── __init__.py
│   ├── chart_card.py           # Standardized card wrapper with hover modebars
│   ├── dispatch_panel.py       # Prescriptive Haversine rebalancing transfer cards
│   ├── filter_panel.py         # Dropdowns (User, Region), toggle, slider, and export button
│   └── station_inspector.py    # Deep-dive station profile inspector card
│
├── charts/
│   ├── __init__.py
│   ├── geo_map.py              # Map with corridor lines & dynamic regional auto-centering
│   ├── station_analysis.py     # Top Stations, Imbalance Diverging Bar & Leisure Hotspots
│   └── trip_analysis.py        # Top Corridors horizontal ranking bar chart
│
├── utils/
│   ├── __init__.py
│   ├── data_processing.py      # Analytical engine (Haversine, regions, metrics, deep-dive)
│   └── theme.py                # Plotly dark theme and graceful empty-state figure generator
│
├── assets/
│   └── style.css               # Scoped dark theme stylesheet with responsive CSS grid
│
└── tests/
    ├── test_analytics.py       # 7 unit tests for mathematical correctness & edge cases
    ├── test_full_pipeline.py   # Full pipeline test against 174,738 master records
    ├── test_advanced_features.py # Verification for 7 advanced capabilities
    └── verify_chart_fixes.py   # Verification for label formatting & monotonic sorting
```

---

## 🚀 Quick Start

### 1. Installation
Ensure Python 3.10+ is installed, then install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run Dashboard
```bash
python app.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:8050/`**

---

## 🔗 Team Integration Guide (Members 3 & 4)

To merge Member 5 into the collaborative master dashboard:

```python
from member5.layout import create_layout
from member5.callbacks.dashboard_callbacks import register_callbacks

# 1. Embed Member 5 section inside your main dashboard layout:
team_app.layout = html.Div([
    # ... Member 3 KPIs & Filters ...
    # ... Member 4 Time Analysis ...
    create_layout(),  # Member 5 Station & Trip Analysis
])

# 2. Register Member 5 callbacks onto the shared team Dash app:
register_callbacks(team_app)
```

All component IDs in this module use the isolated `m5-*` prefix (`m5-user-filter`, `m5-region-filter`, `m5-top-n-slider`, `m5-station-map`, etc.), guaranteeing zero namespace collisions.

---

## 🧪 Automated Testing

Run the test suite to verify analytical math, pipeline health, and all 7 advanced features:
```bash
python tests/test_analytics.py
python tests/test_full_pipeline.py
python tests/test_advanced_features.py
python tests/verify_chart_fixes.py
```
All tests report `[PASS]`.
