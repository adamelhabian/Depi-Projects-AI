# Ford GoBike Enterprise Master BI Analytics Platform

A unified, production-grade Business Intelligence platform integrating the complete Ford GoBike analytical suite into an executive portal powered by Supabase Cloud PostgreSQL.

---

## 🌟 Overview & Architecture

The **Master Dashboard** acts as the central intelligence gateway for the Ford GoBike project, consolidating independent member analytical modules into a coherent multi-page portal:

1. **Executive Overview (`/`)**: Fleet KPI summary cards, operational volume overview, executive key insights, and rapid module launcher cards.
2. **Station & Network Flow (`/stations`)**: Geospatial routing, top station hubs, corridor traffic volumes, station flow imbalances (**Member 5**), and interactive right-side station deep-dive drawer.
3. **Time & Rider Demographics (`/time-user`)**: Diurnal rush-hour rhythms, weekly usage patterns, membership split (Donut chart), and age cohort distributions (**Member 4**).
4. **User Trips Explorer (`/user-trips`)**: Raw trip record exploration, pagination, and multi-criteria filtering table (**Member 3**).

```
                      ┌───────────────────────────────────────┐
                      │    Supabase Cloud PostgreSQL (Gold)   │
                      └──────────────────┬────────────────────┘
                                         │
                     ┌───────────────────┼───────────────────┐
        ┌────────────▼─────────────┐     │     ┌─────────────▼────────────┐
        │  station-trip-analysis   │     │     │    time-user-analysis    │
        │ (Standalone or Integrated)│     │     │(Standalone or Integrated)│
        └────────────┬─────────────┘     │     └─────────────┬────────────┘
                     │                   │                   │
                     └───────────────────┼───────────────────┘
                                         │
                      ┌──────────────────▼────────────────────┐
                      │            master-dashboard           │
                      │  - Collapsible Executive Sidebar      │
                      │  - Sticky Global Filter Bar & Export  │
                      │  - Fast Parquet In-Memory Cache Layer │
                      │  - URL Routing & Dynamic Loading      │
                      └───────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
master-dashboard/
├── .env                          # Supabase PostgreSQL connection string
├── .gitignore                    # Python, bytecode, and cache exclusions
├── requirements.txt              # Production dependencies
├── config.py                     # Centralized settings, routes, and component IDs
├── data_loader.py                # Supabase direct ingestion & parquet caching layer
├── README.md                     # Architecture and execution guide
├── app.py                        # Central Dash entry point
├── layout.py                     # Master shell layout (Sidebar + Navbar + Global Filter Bar)
├── assets/
│   └── master_style.css          # Master design system, scrollbars, drawer & transitions
├── components/
│   ├── __init__.py
│   ├── sidebar.py                # Collapsible executive navigation sidebar
│   ├── navbar.py                 # Breadcrumb header with live cloud status
│   ├── global_filter_bar.py      # Sticky cross-module global filter bar & export summary
│   ├── kpi_banner.py             # Fleet-wide executive KPI banner
│   ├── key_insights.py           # Data-driven executive insight cards
│   └── footer.py                 # Application attribution footer
├── pages/
│   ├── __init__.py
│   ├── overview.py               # Executive summary landing page
│   ├── station_page.py           # Integration view for Station & Network Flow
│   ├── time_user_page.py         # Integration view for Time & Rider Demographics
│   └── user_trips_page.py        # Integration view for User Trips Explorer
├── callbacks/
│   ├── __init__.py
│   ├── routing.py                # URL router & sidebar state persistence
│   ├── global_filter_callbacks.py# Global filter bridge & cross-module synchronization
│   ├── export_callbacks.py       # Global data export downloader
│   └── overview_callbacks.py     # Executive overview interactivity
├── utils/
│   ├── __init__.py
│   ├── module_loader.py          # Isolated namespace submodule loader & cache manager
│   └── metrics_calculator.py     # High-efficiency pre-aggregated data cubes
└── tests/
    ├── __init__.py
    ├── test_master_structure.py  # Comprehensive structural & callback graph test suite
    ├── test_phase5_performance.py# Caching speed & render profiler verification
    ├── test_phase3_phase4.py     # Theme, color scale & drawer test suite
    └── test_filter_reactivity_a_to_z.py # End-to-end filter propagation test
```

---

## 🚀 Quickstart & Execution

### 1. Install Dependencies
Ensure you have the required packages installed:
```bash
pip install -r requirements.txt
```

### 2. Verify Cloud Connection
Verify that `.env` contains your Supabase database URI:
```env
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<dbname>
```

### 3. Launch the Master Platform
Run the master application from the `master-dashboard/` folder:
```bash
python app.py
```
Open your browser at **`http://127.0.0.1:8050`**.

---

## ⚡ Performance & Caching

- **Fast Parquet In-Memory Storage**: Station & time-user datasets are cached locally in Parquet format, eliminating repeated 40s cold database queries and enabling instantaneous (<50ms) warm slicing.
- **Symmetric Diverging Color Palette**: Shared theme color scale:
  - Deficit (net < 0): Orange (`#F97316`)
  - Balanced (net = 0): Light Grey (`#94A3B8`)
  - Surplus (net > 0): Blue (`#3B82F6`)
- **Persistent Sidebar**: Sidebar expanded/collapsed state persists across page navigation and browser tabs via `localStorage`.

---

## 🛡️ Zero Collision & Isolation Guarantee

- **Component IDs**:
  - Master Dashboard uses `master-*` IDs.
  - Member 5 uses `m5-*` IDs.
  - Member 4 uses `tu-*` IDs.
  - **Zero ID clashes occur during callback execution**.
- **Source Code Protection**:
  - `station-trip-analysis` and `time-user-analysis` codebases remain isolated and functional.

---

## 🧪 Testing & Verification

Run the automated verification suite:
```bash
python tests/test_master_structure.py
python tests/test_phase5_performance.py
```
This verifies:
1. Environment and database connectivity.
2. Isolated submodule namespace loading.
3. Fast Parquet cache retrieval times (<50ms).
4. Full Dash application callback graph registration (20 callbacks).
