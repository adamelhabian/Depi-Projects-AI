# Ford GoBike Enterprise Master BI Analytics Platform

A unified, production-grade Business Intelligence platform integrating the complete Ford GoBike analytical suite into an executive portal powered by Supabase Cloud PostgreSQL.

---

## 🌟 Overview & Architecture

The **Master Dashboard** acts as the central intelligence gateway for the Ford GoBike project, consolidating independent member analytical modules into a coherent multi-page portal:

1. **Executive Overview (`/`)**: Cross-cutting fleet KPI summary cards, operational volume overview, and rapid module launcher cards.
2. **Station & Network Flow (`/stations`)**: Geospatial routing, top station hubs, corridor traffic volumes, and station flow imbalances (**Member 5**).
3. **Time & Rider Demographics (`/time-user`)**: Diurnal rush-hour rhythms, weekly usage patterns, membership split (Donut chart), and age cohort distributions (**Member 4**).

```
                      ┌───────────────────────────────────────┐
                      │    Supabase Cloud PostgreSQL (Gold)   │
                      └──────────────────┬────────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
       ┌────────────▼─────────────┐              ┌────────────▼─────────────┐
       │  station-trip-analysis   │              │   time-user-analysis     │
       │ (Standalone or Integrated)│             │(Standalone or Integrated)│
       └────────────┬─────────────┘              └────────────┬─────────────┘
                    │                                         │
                    └────────────────────┬────────────────────┘
                                         │
                      ┌──────────────────▼────────────────────┐
                      │            master-dashboard           │
                      │  - Executive Navigation Sidebar       │
                      │  - URL Routing (dcc.Location)         │
                      │  - Unified KPIs & Live Cloud Sync     │
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
├── data_loader.py                # Direct Supabase data ingestion layer
├── README.md                     # Architecture and execution guide
├── app.py                        # Central Dash entry point
├── layout.py                     # Master shell layout (Sidebar + Navbar + Page Container)
├── assets/
│   └── master_style.css          # Custom styling, scrollbars, and transitions
├── components/
│   ├── __init__.py
│   ├── sidebar.py                # Responsive executive navigation sidebar
│   ├── navbar.py                 # Breadcrumb header with live cloud status
│   ├── kpi_banner.py             # 4-card fleet-wide KPI banner
│   └── footer.py                 # Application attribution footer
├── pages/
│   ├── __init__.py
│   ├── overview.py               # Executive summary landing page
│   ├── station_page.py           # Integration view for Station Analysis
│   └── time_user_page.py         # Integration view for Time & User Analysis
├── callbacks/
│   ├── __init__.py
│   └── routing.py                # URL router and active state synchronization
├── utils/
│   ├── __init__.py
│   └── module_loader.py          # Isolated namespace submodule loader
└── tests/
    ├── __init__.py
    └── test_master_structure.py  # Comprehensive verification test suite
```

---

## 🚀 Quickstart & Execution

### 1. Install Dependencies
Ensure you have the required packages installed:
```bash
pip install -r requirements.txt
```

### 2. Verify Cloud Connection
Verify that `.env` contains the valid Supabase database URI:
```env
DATABASE_URL=postgresql://postgres.mvolsievttmxgwbkuovy:ford-gobike1234@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
```

### 3. Launch the Master Platform
Run the master application from the `master-dashboard/` folder:
```bash
python app.py
```
Open your browser at **`http://127.0.0.1:8050`**.

---

## 🛡️ Zero Collision & Isolation Guarantee

- **Component IDs**:
  - Master Dashboard uses `master-*` IDs.
  - Member 5 uses `m5-*` IDs.
  - Member 4 uses `tu-*` IDs.
  - **Zero ID clashes occur during callback execution**.
- **Source Code Protection**:
  - `station-trip-analysis` and `time-user-analysis` codebases remain 100% untouched.
  - Each module can still run standalone via its own `python app.py`.

---

## 🧪 Testing & Verification

Run the automated verification suite:
```bash
python tests/test_master_structure.py
```
This tests:
1. Environment and database connectivity.
2. Dynamic module loading under isolated namespaces.
3. Rendering of all 3 page layouts (`/`, `/stations`, `/time-user`).
4. Full Dash application callback graph registration.
