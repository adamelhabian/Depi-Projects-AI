# Ford GoBike Analytics — Station & Trip Analysis (Member 5)

> **Collaborative Data Analytics Project | DEPI Final Project**  
> Modern, interactive geospatial analytics, transit corridor flow mapping, spatial fleet rebalancing dispatch, and station deep-dive profiling built with **Dash**, **Plotly**, and **Tailwind CSS**.

---

## 👥 Team Responsibilities

| Role | Member | Scope |
|---|---|---|
| Member 1 | Database Engineering | PostgreSQL Database Architecture, Views & SQL Pipeline |
| Member 2 | Data Engineering | Data Cleaning, Pipeline Processing & Master Datasets |
| Member 3 | BI & KPI Design | High-Level KPI Tiles, Global Filters & Executive Metrics |
| Member 4 | Behavioral Analytics | Time-Series Trends, Peak Hours & User Demographics |
| **Member 5** | **Station & Trip Analysis** | **Network Traffic Hubs, Flow Corridors, Rebalancing & Station Deep Dives** |

---

## 🚀 Key Features & Capabilities

### 1. Station Traffic & Flow Corridor Map
* **Dynamic Circle Markers**: Radius proportional to total traffic ($\text{Departures} + \text{Arrivals}$); color represents Net Flow (Emerald Green = Inbound Surplus, Crimson Red = Outbound Deficit).
* **Flow Corridor Transit Lines**: Visualizes top origin–destination routes directly over the map with line thickness and opacity reflecting trip density.
* **Smart Click-to-Inspect**: Clicking any station circle on the map or bar in the ranking charts opens the Station Deep Dive Side Drawer.

### 2. Interactive Station Deep Dive Side Drawer
* **Slide-In Map Drawer**: Elegant floating panel overlaying the map with smooth CSS slide transitions.
* **Station Header**: Station name, regional badge (`SF`, `EB`, `SJ`), regional traffic rank, and close button.
* **Dual KPI Summary Tiles**: Total trips (with network share %) and Net Imbalance (with status badge).
* **Trip Flow Split Bar**: Stacked proportional visualization of Inbound vs. Outbound flow with exact journey counts.
* **Top 3 Connected Destinations**: Ranked list of the station's highest-volume journey destinations.
* **Round-Trip Ratio & Rebalancing Suggestion**: Percentage of loop journeys starting and ending at the dock, paired with automated operational guidance.
* **"Focus Map on Station" Action**: Re-centers and zooms the map directly onto the selected station.

### 3. Flexible Top Ranking Scope (Step = 1)
* **Continuous Range Slider**: Allows selecting **any integer from 1 to 30** (`TOP_N_STEP = 1`) without arbitrary jump constraints.
* **Live Dynamic Badge & Tooltip**: Instant real-time label updates (`Top 7`, `Top 13`, `Top 24`).
* **Auto-Expanding Chart Cards**: Cards dynamically adapt their height (`max(340, n_bars * 28 + 60)`) to eliminate bar overlap and squishing.

### 4. Strictly Ordered Analytical Charts
* **Top Stations by Total Traffic**: Ranked descending from highest volume at the top, styled with rank-opacity gradients.
* **Top Origin–Destination Corridors**: Clean single-line route labels with standard typography arrows (`→`).
* **Station Network Flow Imbalance**: Diverging horizontal bar chart strictly descending from highest surplus down to largest deficit. Dynamically partitions odd and even Top-N scopes.
* **Leisure & Tourism Hotspots**: Highlights loop journeys ($\text{start} == \text{end}$) indicative of scenic and recreational riding (e.g. Golden Gate Park docks), filtered for statistically significant volume.

### 5. Prescriptive Smart Fleet Rebalancing Dispatch
* **Algorithmic Haversine Spatial Matching**: Automatically pairs high-deficit docks with their nearest high-surplus neighbor within the same metropolitan cluster.
* **Actionable Truck Dispatch Cards**: Specifies exact recommended transfer quantities ($\text{Net Flow} // 2$) and spatial distance in kilometers.

### 6. Professional SVG Icon System (Zero Emojis)
* **Self-Contained SVG Library**: Built in `components/icons.py` using SVG data URIs.
* **100% Dash-Native & Dependency-Free**: No external font files or third-party component wrappers needed.

### 7. High-Performance Data Layer (Supabase + Smart Fallback)
* **Direct Cloud Ingestion**: Queries `gold.trip_analytics` directly from Supabase PostgreSQL database in ~2-3 seconds.
* **Resilient Offline Fallback**: Automatically switches to local CSV if internet or credentials are unavailable.

---

## 📐 Analytical Math & Rules

$$\text{Total Traffic} = \text{Departures} + \text{Arrivals}$$

$$\text{Net Flow} = \text{Arrivals} - \text{Departures}$$

$$\text{Flow Imbalance Ratio (\%)} = \left(\frac{|\text{Net Flow}|}{\text{Total Traffic}}\right) \times 100$$

* **Canonical Station Grouping**: Stations are grouped strictly by name. GPS coordinates are computed via median position to prevent duplication caused by sensor drift.
* **Coordinate Independence**: Stations missing GPS coordinates remain fully ranked in all bar charts; they are excluded only from the spatial map.
* **Strict Classification**:
  * $\text{Outbound Deficit} \implies \text{Net Flow} < 0$
  * $\text{Inbound Surplus} \implies \text{Net Flow} > 0$

---

## 📁 Repository Structure

```text
station-trip-analysis/
├── app.py                      # Dash application entry point & local development server
├── config.py                   # Central theme colors, region presets, and component IDs
├── data_loader.py              # Supabase cloud loader with caching & CSV fallback
├── layout.py                   # Master Tailwind CSS layout (Controls -> Map/Drawer -> Charts -> Dispatch)
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation & integration guide
│
├── callbacks/
│   ├── __init__.py
│   └── dashboard_callbacks.py  # Reactive controller for filters, inspector drawer, and export
│
├── components/
│   ├── __init__.py
│   ├── chart_card.py           # Clean white card wrapper with dynamic card height
│   ├── dispatch_panel.py       # Smart rebalancing dispatch recommendation cards
│   ├── filter_panel.py         # Tailwind 12-column filter bar with flexible slider
│   ├── icons.py                # Standalone SVG data URI icon library (no emojis)
│   └── station_inspector.py    # Slide-in deep-dive station profile drawer
│
├── charts/
│   ├── __init__.py
│   ├── geo_map.py              # Mapbox scatter map with corridor transit arcs
│   ├── station_analysis.py     # Top Stations, Flow Imbalance & Leisure Hotspots
│   └── trip_analysis.py        # Top Corridors horizontal ranking chart
│
├── utils/
│   ├── __init__.py
│   ├── data_processing.py      # Analytical engine (Haversine, regions, metrics, deep-dive)
│   └── theme.py                # Plotly clean light theme & empty state builder
│
└── tests/
    ├── test_analytics.py       # 7 unit tests for mathematical correctness & edge cases
    ├── test_full_pipeline.py   # End-to-end pipeline validation on 174k+ trips
    ├── test_advanced_features.py # Validation for regional clusters, deep dive & dispatch
    └── verify_chart_fixes.py   # Verification for descending order & distinct station names
```

---

## 🚀 Quick Start Guide

### 1. Clone / Checkout Branch
```bash
git fetch origin
git checkout feat/station-trip-analysis
git pull origin feat/station-trip-analysis
```

### 2. Navigate to Directory
```bash
cd Data-Analysis/ford_gobike_analysis/dashboard/station-trip-analysis
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database Credentials (Optional for Live Supabase)
Ensure your `.env` file in this directory contains:
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres
```
*(If no `.env` is supplied, the loader gracefully loads local CSV data).*

### 5. Launch Dashboard
```bash
python app.py
```
Open your browser at:
👉 **`http://127.0.0.1:8050/`**

---

## 🔗 Team Integration Guide (Members 3 & 4)

To embed this module into the collaborative team master dashboard:

```python
from member5.layout import create_layout
from member5.callbacks.dashboard_callbacks import register_callbacks

# 1. Embed Member 5 section into the master dashboard layout:
main_layout.children.append(create_layout())

# 2. Register Member 5 reactive callbacks onto the shared Dash instance:
register_callbacks(team_app)
```

> **Isolation Guarantee**: All component IDs use the unique `m5-*` prefix (`m5-user-filter`, `m5-top-n-slider`, `m5-station-map`, `m5-inspector-container`, etc.), guaranteeing zero collisions with other team sections.

---

## 🧪 Automated Testing

Run the comprehensive test suite locally:
```bash
python tests/test_analytics.py
python tests/test_advanced_features.py
python tests/test_full_pipeline.py
python tests/verify_chart_fixes.py
```
All tests should return `[PASS]`.
