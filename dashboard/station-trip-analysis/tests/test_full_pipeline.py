"""
tests/test_full_pipeline.py – End-to-End Pipeline Verification on Real Dataset
==============================================================================
"""

import sys
from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent.parent
if str(_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_MODULE_DIR))

from data_loader import load_clean_data
from utils.data_processing import (
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


def run_full_pipeline_test():
    print("Loading full dataset via load_clean_data()...")
    df = load_clean_data()
    print(f"[PASS] Dataset loaded: {len(df):,} trips across {len(df.columns)} columns.")

    # Verify no 'nan' in generated route
    invalid_routes = df["route"].dropna().str.contains(r"\bnan\b", case=False, regex=True)
    assert not invalid_routes.any(), "Fake 'nan' route detected in dataset!"
    print("[PASS] Route integrity verified: zero 'nan' routes.")

    # Canonical station metrics
    print("Computing canonical station metrics...")
    station_metrics = compute_canonical_station_metrics(df)
    n_stations = len(station_metrics)
    print(f"[PASS] Canonical station metrics computed: {n_stations} unique active stations.")

    # Verify station name uniqueness
    assert station_metrics["station_name"].nunique() == n_stations, "Duplicate station names found in metrics!"
    print("[PASS] Station name uniqueness verified.")

    # Verify math consistency
    assert (station_metrics["total_traffic"] == station_metrics["departures"] + station_metrics["arrivals"]).all(), "Total traffic math mismatch!"
    assert (station_metrics["net_flow"] == station_metrics["arrivals"] - station_metrics["departures"]).all(), "Net flow math mismatch!"
    print("[PASS] Total traffic and Net Flow mathematical consistency verified.")

    # Top Stations
    top_stations = compute_top_stations(station_metrics, top_n=10)
    assert len(top_stations) == 10, f"Expected 10 top stations, got {len(top_stations)}"
    assert top_stations["total_traffic"].is_monotonic_decreasing, "Top stations should be sorted descending (Rank 1 first)!"
    print(f"[PASS] Top stations computed (Max traffic = {top_stations['total_traffic'].max():,}).")

    # Top Routes
    top_routes = compute_top_routes(df, top_n=10)
    assert len(top_routes) == 10, f"Expected 10 top routes, got {len(top_routes)}"
    assert top_routes["trip_count"].is_monotonic_decreasing, "Top routes should be sorted descending (highest volume first)!"
    print(f"[PASS] Top routes computed (Top corridor trips = {top_routes['trip_count'].max():,}).")

    # Flow Imbalance
    imbalance = compute_flow_imbalance(station_metrics, top_n=10)
    assert len(imbalance) == 10, f"Expected 10 imbalance stations, got {len(imbalance)}"
    deficits = imbalance[imbalance["net_flow"] < 0]
    surpluses = imbalance[imbalance["net_flow"] > 0]
    assert len(deficits) > 0 and len(surpluses) > 0, "Both deficit and surplus stations should be present!"
    assert (deficits["imbalance_type"] == "Outbound Deficit").all()
    assert (surpluses["imbalance_type"] == "Inbound Surplus").all()
    print(f"[PASS] Flow imbalance computed ({len(deficits)} Outbound Deficit, {len(surpluses)} Inbound Surplus).")

    # Chart Generation
    print("Testing figure generation across all 4 visualizations...")
    fig_map = create_station_map(station_metrics)
    fig_stations = create_top_stations_chart(top_stations)
    fig_routes = create_top_routes_chart(top_routes)
    fig_imbalance = create_flow_imbalance_chart(imbalance)

    for name, fig in [
        ("Station Traffic & Flow Map", fig_map),
        ("Top Stations by Total Traffic", fig_stations),
        ("Top Origin-Destination Corridors", fig_routes),
        ("Station Network Flow Imbalance", fig_imbalance),
    ]:
        assert fig is not None, f"Figure {name} is None!"
        assert len(fig.data) > 0, f"Figure {name} has no traces!"
        print(f"[PASS] Figure '{name}' generated successfully.")

    # Filtered test (User Type: Subscriber)
    sub_df = df[df["user_type"] == "Subscriber"]
    sub_metrics = compute_canonical_station_metrics(sub_df)
    sub_top_stations = compute_top_stations(sub_metrics, top_n=5)
    assert len(sub_top_stations) == 5
    print("[PASS] Filtered subset (Subscribers) computed successfully.")

    print("\nALL END-TO-END PIPELINE CHECKS PASSED SUCCESSFULLY!\n")


if __name__ == "__main__":
    run_full_pipeline_test()
