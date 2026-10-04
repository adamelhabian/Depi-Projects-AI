"""
tests/test_analytics.py – Comprehensive Analytical & Edge-Case Tests
=====================================================================
Validates all requirements specified for Member 5:
  1. Total Traffic = Departures + Arrivals
  2. Net Flow = Arrivals - Departures
  3. Strict Deficit (< 0) and Surplus (> 0) classification
  4. No station duplication from varying coordinates
  5. Missing coordinates do NOT drop stations from ranking or imbalance
  6. Route generation produces no 'nan' routes
  7. Empty dataframe handling generates empty figures without crashing
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add member5 module root to path
_MODULE_DIR = Path(__file__).resolve().parent.parent
if str(_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_MODULE_DIR))

from utils.data_processing import (
    normalize_station_name,
    generate_routes,
    compute_canonical_station_metrics,
    compute_top_stations,
    compute_top_routes,
    compute_flow_imbalance,
    compute_active_stations_count,
)
from charts.geo_map import create_station_map
from charts.station_analysis import (
    create_top_stations_chart,
    create_flow_imbalance_chart,
)
from charts.trip_analysis import create_top_routes_chart


def test_station_normalization():
    raw = pd.Series([" Market St ", "None", "nan", "", None, "Powell St", "NULL"])
    clean = normalize_station_name(raw)
    assert clean[0] == "Market St", f"Expected 'Market St', got {clean[0]}"
    assert pd.isna(clean[1]), f"Expected NA for 'None', got {clean[1]}"
    assert pd.isna(clean[2]), f"Expected NA for 'nan', got {clean[2]}"
    assert pd.isna(clean[3]), f"Expected NA for empty string, got {clean[3]}"
    assert pd.isna(clean[4]), f"Expected NA for None, got {clean[4]}"
    assert clean[5] == "Powell St", f"Expected 'Powell St', got {clean[5]}"
    assert pd.isna(clean[6]), f"Expected NA for 'NULL', got {clean[6]}"
    print("[PASS] Station normalization passed.")


def test_route_generation():
    df = pd.DataFrame({
        "start_station_name": ["Station A", "Station B", pd.NA, "Station C"],
        "end_station_name": ["Station B", pd.NA, "Station A", "Station D"],
    })
    routes = generate_routes(df)
    assert routes[0] == "Station A → Station B", f"Expected 'Station A → Station B', got {routes[0]}"
    assert pd.isna(routes[1]), f"Expected NA for incomplete route, got {routes[1]}"
    assert pd.isna(routes[2]), f"Expected NA for incomplete route, got {routes[2]}"
    assert routes[3] == "Station C → Station D", f"Expected 'Station C → Station D', got {routes[3]}"
    assert not any("nan" in str(r).lower() for r in routes.dropna()), "Fake 'nan' route found!"
    print("[PASS] Route generation passed (no fake 'nan' routes).")


def test_station_aggregation_and_math():
    # Prompt example:
    # Station A: 10 departures, 20 arrivals -> total_traffic = 30, net_flow = +10
    # Station B: 20 departures, 5 arrivals  -> total_traffic = 25, net_flow = -15
    data = []
    # 10 trips A -> C
    for _ in range(10):
        data.append({"start_station_name": "Station A", "end_station_name": "Station C",
                     "start_station_latitude": 37.77, "start_station_longitude": -122.41,
                     "end_station_latitude": 37.78, "end_station_longitude": -122.40})
    # 20 trips C -> A
    for _ in range(20):
        data.append({"start_station_name": "Station C", "end_station_name": "Station A",
                     "start_station_latitude": 37.78, "start_station_longitude": -122.40,
                     "end_station_latitude": 37.77, "end_station_longitude": -122.41})
    # 20 trips B -> C
    for _ in range(20):
        data.append({"start_station_name": "Station B", "end_station_name": "Station C",
                     "start_station_latitude": 37.76, "start_station_longitude": -122.42,
                     "end_station_latitude": 37.78, "end_station_longitude": -122.40})
    # 5 trips C -> B
    for _ in range(5):
        data.append({"start_station_name": "Station C", "end_station_name": "Station B",
                     "start_station_latitude": 37.78, "start_station_longitude": -122.40,
                     "end_station_latitude": 37.76, "end_station_longitude": -122.42})

    df = pd.DataFrame(data)
    metrics = compute_canonical_station_metrics(df).set_index("station_name")

    # Station A: 10 dep, 20 arr
    assert metrics.loc["Station A", "departures"] == 10
    assert metrics.loc["Station A", "arrivals"] == 20
    assert metrics.loc["Station A", "total_traffic"] == 30
    assert metrics.loc["Station A", "net_flow"] == 10

    # Station B: 20 dep, 5 arr
    assert metrics.loc["Station B", "departures"] == 20
    assert metrics.loc["Station B", "arrivals"] == 5
    assert metrics.loc["Station B", "total_traffic"] == 25
    assert metrics.loc["Station B", "net_flow"] == -15

    print("[PASS] Canonical aggregation and arithmetic (Traffic = Dep + Arr, Flow = Arr - Dep) passed.")


def test_coordinate_variations_do_not_duplicate_stations():
    # Same station with slightly different GPS coordinates
    df = pd.DataFrame({
        "start_station_name": ["Station A", "Station A", "Station A"],
        "end_station_name": ["Station B", "Station B", "Station B"],
        "start_station_latitude": [37.7701, 37.7702, 37.7700],
        "start_station_longitude": [-122.4101, -122.4102, -122.4100],
        "end_station_latitude": [37.7801, 37.7802, 37.7800],
        "end_station_longitude": [-122.4001, -122.4002, -122.4000],
    })
    metrics = compute_canonical_station_metrics(df)
    assert len(metrics) == 2, f"Expected exactly 2 stations, but got {len(metrics)} (duplicate rows created!)"
    print("[PASS] Duplicate coordinate variation test passed (no duplicate station rows).")


def test_missing_coordinates_do_not_drop_stations():
    df = pd.DataFrame({
        "start_station_name": ["Station With Coords", "Station Without Coords"],
        "end_station_name": ["Station With Coords", "Station Without Coords"],
        "start_station_latitude": [37.77, np.nan],
        "start_station_longitude": [-122.41, np.nan],
        "end_station_latitude": [37.77, np.nan],
        "end_station_longitude": [-122.41, np.nan],
    })
    metrics = compute_canonical_station_metrics(df)
    assert len(metrics) == 2, "Station without coords was dropped from metrics!"
    top_stations = compute_top_stations(metrics, top_n=10)
    assert "Station Without Coords" in top_stations["station_name"].values, "Station without coords was dropped from Top Stations!"
    print("[PASS] Missing coordinates handling passed (stations preserved in ranking).")


def test_flow_imbalance_classification():
    # Test strict < 0 for deficit and > 0 for surplus
    metrics = pd.DataFrame({
        "station_name": ["Deficit 1", "Deficit 2", "Neutral", "Surplus 1", "Surplus 2"],
        "departures": [100, 50, 20, 10, 5],
        "arrivals":   [10,  20, 20, 80, 95],
        "total_traffic": [110, 70, 40, 90, 100],
        "net_flow": [-90, -30, 0, +70, +90],
    })
    imbalance = compute_flow_imbalance(metrics, top_n=10)

    # Check deficit side
    def_rows = imbalance[imbalance["net_flow"] < 0]
    sur_rows = imbalance[imbalance["net_flow"] > 0]
    neutral_rows = imbalance[imbalance["net_flow"] == 0]

    assert len(def_rows) == 2
    assert len(sur_rows) == 2
    assert len(neutral_rows) == 0, "Zero net_flow station should not appear in deficit or surplus!"
    assert set(def_rows["station_name"]).isdisjoint(set(sur_rows["station_name"])), "Station appeared in both!"
    print("[PASS] Flow imbalance strict classification passed.")


def test_empty_dataframe_does_not_crash_charts():
    empty_df = pd.DataFrame()
    empty_metrics = compute_canonical_station_metrics(empty_df)
    top_stations = compute_top_stations(empty_metrics, 10)
    top_routes = compute_top_routes(empty_df, 10)
    imbalance = compute_flow_imbalance(empty_metrics, 10)

    fig1 = create_station_map(empty_metrics)
    fig2 = create_top_stations_chart(top_stations)
    fig3 = create_top_routes_chart(top_routes)
    fig4 = create_flow_imbalance_chart(imbalance)

    assert fig1 is not None and hasattr(fig1, "to_dict")
    assert fig2 is not None and hasattr(fig2, "to_dict")
    assert fig3 is not None and hasattr(fig3, "to_dict")
    assert fig4 is not None and hasattr(fig4, "to_dict")
    print("[PASS] Empty dataframe graceful degradation passed.")


if __name__ == "__main__":
    print("\nRunning Member 5 Analytical Verification Suite...")
    test_station_normalization()
    test_route_generation()
    test_station_aggregation_and_math()
    test_coordinate_variations_do_not_duplicate_stations()
    test_missing_coordinates_do_not_drop_stations()
    test_flow_imbalance_classification()
    test_empty_dataframe_does_not_crash_charts()
    print("\nALL 7 TESTS PASSED SUCCESSFULLY! 100% CORRECT.\n")
