"""
tests/test_master_structure.py – Master Dashboard Verification Suite
===================================================================
Tests configuration, direct Supabase cloud ingestion, dynamic submodule
loading under isolated namespaces, page view rendering, and unified Dash callbacks.
"""

import sys
from pathlib import Path

# Ensure master-dashboard root is on sys.path
_CURRENT_DIR = Path(__file__).resolve().parent.parent
if str(_CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(_CURRENT_DIR))

import pandas as pd
from dash import Dash, html
from config import APP_TITLE, ROUTE_OVERVIEW, ROUTE_STATIONS, ROUTE_TIME_USER
from data_loader import check_db_health, load_master_kpi_summary
from utils.module_loader import get_station_module, get_time_user_module
from pages.overview import render_overview_page
from pages.station_page import render_station_page
from pages.time_user_page import render_time_user_page
from layout import create_master_layout
from callbacks.routing import register_routing_callbacks


def test_master_dashboard_suite():
    print("\n" + "=" * 65)
    print("Running Master Dashboard Structural & Integration Verification")
    print("=" * 65)

    # 1. Supabase Cloud Connection & Executive KPIs
    print(">> 1. Testing Supabase Cloud Health & Executive KPI Ingestion...")
    health = check_db_health()
    assert health["status"] == "healthy", f"Database health check failed: {health}"
    assert health["total_records"] > 100000, f"Expected >100k records, got {health['total_records']}"
    print(f"   [PASS] Connected to Supabase! Found {health['total_records']:,} records (Latency: {health['latency_ms']}ms).")

    kpis = load_master_kpi_summary()
    assert "total_trips" in kpis and "unique_stations" in kpis
    assert "%" in kpis["subscriber_pct"]
    print(f"   [PASS] Executive KPIs verified: {kpis}")

    # 2. Submodule Dynamic Namespace Loading
    print(">> 2. Testing Dynamic Submodule Loading with Isolated Namespaces...")
    st_layout_fn, st_cb_fn = get_station_module()
    assert callable(st_layout_fn) and callable(st_cb_fn)
    print("   [PASS] Member 5 (Station Analysis) module successfully loaded.")

    tu_layout_fn, tu_cb_fn = get_time_user_module()
    assert callable(tu_layout_fn) and callable(tu_cb_fn)
    print("   [PASS] Member 4 (Time & User Analysis) module successfully loaded.")

    # 3. Page Views Rendering
    print(">> 3. Testing Master Multi-Page Rendering...")
    overview_view = render_overview_page()
    assert overview_view is not None
    print("   [PASS] Executive Overview page rendered successfully.")

    station_view = render_station_page()
    assert station_view is not None
    print("   [PASS] Station & Network Flow page rendered successfully.")

    time_user_view = render_time_user_page()
    assert time_user_view is not None
    print("   [PASS] Time & Rider Demographics page rendered successfully.")

    # 4. Master App Shell & Callback Registration
    print(">> 4. Testing Master App Shell & Full Callbacks Registration Graph...")
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = create_master_layout()
    assert app.layout is not None
    print("   [PASS] Master App Shell layout created successfully.")

    register_routing_callbacks(app)
    st_cb_fn(app)
    tu_cb_fn(app)
    total_callbacks = len(app.callback_map)
    assert total_callbacks >= 8, f"Expected >= 8 registered callbacks, got {total_callbacks}"
    print(f"   [PASS] Unified Dash Callback Graph registered successfully with {total_callbacks} active callbacks!")

    print("\n" + "=" * 65)
    print("ALL MASTER DASHBOARD CHECKS PASSED (100% SUCCESS)!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    test_master_dashboard_suite()
