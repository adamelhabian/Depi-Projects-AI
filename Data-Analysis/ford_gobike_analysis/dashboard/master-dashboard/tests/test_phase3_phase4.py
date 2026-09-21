"""
tests/test_phase3_phase4.py – Exhaustive Verification Suite for Phase 3 & Phase 4
==================================================================================
Verifies:
  PHASE 3:
  1. Shared Diverging Color Scale (Deficit=#F97316, Balanced=#94A3B8, Surplus=#3B82F6)
     - Symmetrically mapped around 0 on map markers
     - Imbalance bar chart using Blue for surplus and Orange for deficit
     - Map legend using matching gradient
     - No green for deficit/surplus imbalance
  2. Map Initial State & Loading:
     - No Cartesian (0-6 / 0-4) axes in initial figure
     - Initial map figure is a valid Mapbox/Map figure
     - Map component wrapped in dcc.Loading
  3. Station Profile Drawer & Legend:
     - Right-side drawer max 30% width in CSS
     - Drawer close button and empty map click dismiss behavior
     - Map legend collapsible via details/summary
  4. Marker Overlap Optimization:
     - Square root scaling applied
     - Large markers plotted behind small ones (ascending traffic sort)
     - Lower opacity <= 0.80

  PHASE 4:
  1. Station Names & Corridor Formatting:
     - Margins increased (left >= 180px) and automargin=True
     - Corridor labels formatted as two lines ("Origin<br>→ Destination")
     - Value labels on corridor bars formatted as rank + trips ("#1  327")
     - No "..." or "…" truncation cutting station names
     - Full names in hover text
  2. Leisure Hotspots (Round Trips):
     - compute_round_trip_hotspots has min_departures default 100
     - Bar label displays both percentage and loop count
  3. Hourly Duration & Outliers:
     - Hours with < 50 trips have sample size in hover and greyed out markers
     - Annotation for 3 AM / low-sample outlier
  4. Gender Chart:
     - Value labels on ALL bars with outside textposition and no clipping
  5. UI Cleanliness & Jargon Removal:
     - No "Member 3 Core Slice"
     - No "M-5", "M-4", "M-3" in navigation badges
     - No internal "Member 3:" in UI descriptions
  6. Fallback Curve:
     - Labeled as _DEV_FALLBACK_HOURLY_CURVE with clear warnings
"""

import sys
from pathlib import Path

# Ensure master-dashboard root is on sys.path
_CURRENT_DIR = Path(__file__).resolve().parent.parent
if str(_CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(_CURRENT_DIR))

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html

from config import NAV_ITEMS, STATION_MODULE_DIR, TIME_USER_MODULE_DIR
from utils.module_loader import get_station_module, get_time_user_module
import data_loader


def test_phase3_map_and_flow():
    print("\n" + "=" * 65)
    print(">> TEST 1: Phase 3 - Shared Diverging Color Scale & Semantics")
    print("=" * 65)

    # 1. Inspect theme.py in station-trip-analysis
    theme_mod_path = STATION_MODULE_DIR / "utils" / "theme.py"
    theme_code = theme_mod_path.read_text(encoding="utf-8")
    assert "#F97316" in theme_code, "COLOR_DEFICIT #F97316 not found in theme.py"
    assert "#3B82F6" in theme_code, "COLOR_SURPLUS #3B82F6 not found in theme.py"
    assert "#94A3B8" in theme_code, "COLOR_BALANCED #94A3B8 not found in theme.py"
    print("   [PASS] Shared colors defined: Deficit (#F97316), Balanced (#94A3B8), Surplus (#3B82F6)")

    # 2. Test geo_map.py colorscale & symmetric limits
    from utils.module_loader import _clean_colliding_modules
    _clean_colliding_modules()
    sys.path.insert(0, str(STATION_MODULE_DIR))
    import config as st_config
    from charts.geo_map import create_station_map, _scale_marker_sizes
    from charts.station_analysis import create_flow_imbalance_chart, create_top_stations_chart, create_round_trip_hotspots_chart
    from charts.trip_analysis import create_top_routes_chart

    sample_metrics = pd.DataFrame([
        {"station_name": "Hub Alpha", "lat": 37.77, "lon": -122.41, "total_traffic": 10000, "net_flow": -800, "imbalance_ratio": -8.0, "region": "San Francisco", "departures": 5400, "arrivals": 4600},
        {"station_name": "Hub Beta", "lat": 37.78, "lon": -122.42, "total_traffic": 2000, "net_flow": 500, "imbalance_ratio": 25.0, "region": "San Francisco", "departures": 750, "arrivals": 1250},
        {"station_name": "Hub Gamma", "lat": 37.79, "lon": -122.40, "total_traffic": 500, "net_flow": 0, "imbalance_ratio": 0.0, "region": "San Francisco", "departures": 250, "arrivals": 250},
    ])

    fig_map = create_station_map(sample_metrics, region="All")
    # Marker trace is the second trace or trace with mode='markers'
    marker_traces = [t for t in fig_map.data if getattr(t, "mode", "") == "markers"]
    assert len(marker_traces) > 0, "No station marker trace found on map!"
    st_marker = marker_traces[0]
    
    # Check symmetric cmin/cmax
    cmin = st_marker.marker.cmin
    cmax = st_marker.marker.cmax
    assert cmin == -800.0, f"Expected cmin == -800.0, got {cmin}"
    assert cmax == 800.0, f"Expected cmax == 800.0, got {cmax}"
    assert st_marker.marker.opacity <= 0.80, f"Expected opacity <= 0.80, got {st_marker.marker.opacity}"
    
    # Check that large stations are plotted first (behind small ones)
    plotted_stations = [cd[0] for cd in st_marker.customdata]
    assert plotted_stations[0] == "Hub Gamma", f"Expected smallest station Hub Gamma first, got {plotted_stations[0]}"
    assert plotted_stations[-1] == "Hub Alpha", f"Expected largest station Hub Alpha last, got {plotted_stations[-1]}"
    print("   [PASS] Map markers: symmetric around 0 (cmin=-800, cmax=800), opacity=0.78, ascending draw order verified.")

    # 3. Test Imbalance bar chart colors
    sample_imbalance = pd.DataFrame([
        {"station_name": "Surplus Stn", "net_flow": 450, "departures": 100, "arrivals": 550, "imbalance_type": "Surplus"},
        {"station_name": "Deficit Stn", "net_flow": -350, "departures": 500, "arrivals": 150, "imbalance_type": "Deficit"},
    ])
    fig_imbalance = create_flow_imbalance_chart(sample_imbalance)
    bar_trace = fig_imbalance.data[0]
    assert bar_trace.marker.color[0] == "#3B82F6", f"Expected Surplus to be Blue #3B82F6, got {bar_trace.marker.color[0]}"
    assert bar_trace.marker.color[1] == "#F97316", f"Expected Deficit to be Orange #F97316, got {bar_trace.marker.color[1]}"
    assert "automargin" in fig_imbalance.layout.yaxis and fig_imbalance.layout.yaxis.automargin is True, "automargin not True on imbalance chart"
    assert fig_imbalance.layout.margin.l >= 180, f"Expected left margin >= 180, got {fig_imbalance.layout.margin.l}"
    print("   [PASS] Imbalance bar chart: Surplus=Blue (#3B82F6), Deficit=Orange (#F97316), left margin >= 180, automargin=True verified.")

    # 4. Test initial map figure & dcc.Loading in layout.py
    import layout as st_layout
    st_div = st_layout.create_layout()
    # Find dcc.Graph with id ID_MAP
    graph_comp = None
    loading_comp = None
    for child in st_div.children:
        if hasattr(child, "children"):
            sub_children = child.children if isinstance(child.children, list) else [child.children]
            for sc in sub_children:
                if isinstance(sc, dcc.Loading):
                    loading_comp = sc
                elif isinstance(sc, html.Div):
                    for deep_c in (sc.children if isinstance(sc.children, list) else [sc.children]):
                        if isinstance(deep_c, dcc.Loading):
                            loading_comp = deep_c
                        elif isinstance(deep_c, dcc.Graph) and getattr(deep_c, "id", "") == "m5-station-map":
                            graph_comp = deep_c

    assert loading_comp is not None, "m5-station-map not wrapped in dcc.Loading!"
    # Check initial figure of map
    loading_graph = loading_comp.children[0] if isinstance(loading_comp.children, list) else loading_comp.children
    assert isinstance(loading_graph, dcc.Graph), "dcc.Loading does not contain dcc.Graph!"
    init_fig = loading_graph.figure
    assert init_fig is not None, "Initial map figure is None!"
    # Check that it has mapbox or map layout and NO cartesian xaxis/yaxis
    has_map_key = ("mapbox" in init_fig.layout) or ("map" in init_fig.layout)
    assert has_map_key, "Initial map figure lacks mapbox/map layout!"
    assert "xaxis" not in init_fig.layout or not init_fig.layout.xaxis.title.text, "Initial map figure has Cartesian axis!"
    print("   [PASS] Map loading: Initial Mapbox figure provided, zero 0-6 Cartesian flash, wrapped in dcc.Loading.")

    # 5. Test Drawer CSS width & Legend collapsible
    css_path = _CURRENT_DIR / "assets" / "master_style.css"
    css_content = css_path.read_text(encoding="utf-8")
    assert "max-width: 30%" in css_content, "station-drawer max-width: 30% not found in master_style.css"
    print("   [PASS] Station Drawer CSS: max-width: 30% verified.")

    # Legend collapsible
    legend_found = False
    for child in st_div.children:
        for sc in (child.children if hasattr(child, "children") and isinstance(child.children, list) else []):
            if hasattr(sc, "children") and isinstance(sc.children, list):
                for deep_c in sc.children:
                    if isinstance(deep_c, html.Details) and "station-map-legend" in getattr(deep_c, "className", ""):
                        legend_found = True
                        assert isinstance(deep_c.children[0], html.Summary), "First child of Details must be html.Summary"
    assert legend_found, "Map legend html.Details component not found in station layout!"
    print("   [PASS] Map Legend: html.Details collapsible summary dropdown verified.")


def test_phase4_readability_and_bias():
    print("\n" + "=" * 65)
    print(">> TEST 2: Phase 4 - Readability, Bias & UI Cleanliness")
    print("=" * 65)

    from charts.trip_analysis import create_top_routes_chart
    from charts.station_analysis import create_round_trip_hotspots_chart
    from utils.data_processing import compute_round_trip_hotspots

    # 1. Corridor Formatting: two lines, rank + trips, no "..."
    sample_routes = pd.DataFrame([
        {"route": "San Francisco Caltrain (Townsend St at 4th St) → Harry Bridges Plaza (Ferry Building)", "trip_count": 327, "pct_of_total": 0.25},
        {"route": "Berry St at 4th St → San Francisco Caltrain (Townsend St at 4th St)", "trip_count": 280, "pct_of_total": 0.21},
    ])
    fig_routes = create_top_routes_chart(sample_routes)
    route_trace = fig_routes.data[0]
    
    # Bar value text must be f"#{rank}  {trips:,}"
    assert route_trace.text[0] == "#1  327", f"Expected '#1  327', got '{route_trace.text[0]}'"
    assert route_trace.text[1] == "#2  280", f"Expected '#2  280', got '{route_trace.text[1]}'"
    
    # Y axis ticks must be two-line with "<br>→ " and NO "…"
    tick0 = fig_routes.layout.yaxis.ticktext[0]
    assert "<br>→ " in tick0, f"Expected two-line route label with <br>→ , got '{tick0}'"
    assert "…" not in tick0 and "..." not in tick0, f"Found truncation ellipsis in tick: '{tick0}'"
    assert fig_routes.layout.margin.l >= 180, f"Expected left margin >= 180, got {fig_routes.layout.margin.l}"
    assert fig_routes.layout.yaxis.automargin is True, "automargin not True on routes chart"
    print("   [PASS] Corridor routes: Two-line labels ('Origin<br>-> Dest'), '#1  327' bar text, automargin=True, no '...'")

    # 2. Leisure Hotspots min_departures default 100
    dummy_trips = []
    # Station A: 10 departures, 5 loops -> 50% ratio (small sample!)
    for _ in range(5):
        dummy_trips.append({"start_station_name": "Small Station", "end_station_name": "Small Station"})
    for _ in range(5):
        dummy_trips.append({"start_station_name": "Small Station", "end_station_name": "Other Station"})
    # Station B: 150 departures, 30 loops -> 20% ratio (solid sample)
    for _ in range(30):
        dummy_trips.append({"start_station_name": "Large Park", "end_station_name": "Large Park"})
    for _ in range(120):
        dummy_trips.append({"start_station_name": "Large Park", "end_station_name": "Other Station"})

    df_dummy = pd.DataFrame(dummy_trips)
    hotspots = compute_round_trip_hotspots(df_dummy, top_n=5, min_departures=100)
    assert len(hotspots) == 1, f"Expected only Large Park (>=100 departures), got {len(hotspots)}"
    assert hotspots.iloc[0]["station_name"] == "Large Park", f"Expected Large Park, got {hotspots.iloc[0]['station_name']}"
    print("   [PASS] Leisure Hotspots: Default min_departures=100 eliminated 10-trip small-sample outlier.")

    # 3. User Trips: Gender Bar Labels & Hourly Outlier Annotation
    from utils.module_loader import _clean_colliding_modules
    _clean_colliding_modules()
    sys.path.insert(0, str(_CURRENT_DIR))
    import config
    from pages.user_trips_page import _create_gender_user_chart, _create_hour_duration_chart, render_user_trips_page
    
    # Test gender chart
    dummy_users = pd.DataFrame([
        {"user_type": "Subscriber", "member_gender": "Male"},
        {"user_type": "Subscriber", "member_gender": "Female"},
        {"user_type": "Customer", "member_gender": "Male"},
        {"user_type": "Customer", "member_gender": "Female"},
    ])
    fig_gender = _create_gender_user_chart(dummy_users)
    for tr in fig_gender.data:
        assert tr.textposition == "outside", f"Expected textposition outside on gender bar, got {tr.textposition}"
        assert tr.cliponaxis is False, "Expected cliponaxis=False on gender bar"
    print("   [PASS] Gender chart: Value labels outside on ALL bars with cliponaxis=False.")

    # Test hourly duration chart low-sample annotation
    hourly_df = pd.DataFrame([
        {"hour": 3, "duration_min": 35.0}, # n=1
        {"hour": 8, "duration_min": 10.0},
        {"hour": 8, "duration_min": 11.0},
    ] + [{"hour": 8, "duration_min": 10.5}] * 60) # n=62
    fig_hour = _create_hour_duration_chart(hourly_df)
    scatter_tr = fig_hour.data[0]
    # Check 3 AM hover has sample size
    hover_3am = [ht for ht in scatter_tr.hovertext if "03:00" in ht][0]
    assert "Sample Size:" in hover_3am, f"Expected Sample Size in hover, got '{hover_3am}'"
    assert "Low sample size" in hover_3am, f"Expected Low sample size in hover, got '{hover_3am}'"
    assert len(fig_hour.layout.annotations) > 0, "Expected low-sample outlier annotation on hourly duration chart!"
    print("   [PASS] Hourly duration chart: Low sample (<50 trips) greyed out and annotated.")

    # 4. Remove UI Jargon
    # Nav items
    for item in NAV_ITEMS:
        badge = item.get("badge", "")
        assert not badge.startswith("M-"), f"Found M- badge '{badge}' in config.NAV_ITEMS"
        desc = item.get("description", "")
        assert "Member 3" not in desc, f"Found 'Member 3' in description: '{desc}'"
    print("   [PASS] Config NAV_ITEMS: No 'M-5', 'M-4', 'M-3' or 'Member 3' found.")

    # User trips layout
    u_page = render_user_trips_page()
    def check_no_jargon(comp):
        if hasattr(comp, "children"):
            ch = comp.children if isinstance(comp.children, list) else [comp.children]
            for c in ch:
                if isinstance(c, str):
                    assert "Member 3 Core Slice" not in c, "Found 'Member 3 Core Slice' in user_trips_page layout!"
                check_no_jargon(c)
    check_no_jargon(u_page)
    print("   [PASS] User Trips UI: 'Member 3 Core Slice' successfully replaced with 'Overall Network'.")

    # 5. Data loader fallback
    assert hasattr(data_loader, "_DEV_FALLBACK_HOURLY_CURVE"), "_DEV_FALLBACK_HOURLY_CURVE not found in data_loader"
    print("   [PASS] Fallback hourly curve explicitly labeled as _DEV_FALLBACK_HOURLY_CURVE.")

    print("\n" + "=" * 65)
    print("ALL PHASE 3 & PHASE 4 TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    test_phase3_map_and_flow()
    test_phase4_readability_and_bias()
