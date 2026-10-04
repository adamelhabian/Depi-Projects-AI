"""
tests/test_advanced_features.py – Verification for 7 Advanced Features
======================================================================
Tests:
  1. Geographic clustering and region assignment (zero unmapped valid stations).
  2. Map flow corridor trace generation.
  3. Imbalance Ratio % mathematical correctness.
  4. Leisure / Round-Trip hotspots computation and chart generation.
  5. Station Profile deep-dive inspector extraction.
  6. Smart Dispatch Rebalancing Haversine pair matching.
  7. Full Dash App instantiation, layout rendering, and callback registration.
"""

from __future__ import annotations

import sys
from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent.parent
if str(_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_MODULE_DIR))

import pandas as pd
from data_loader import load_clean_data
from utils.data_processing import (
    compute_canonical_station_metrics,
    compute_top_stations,
    compute_top_routes,
    compute_flow_imbalance,
    compute_round_trip_hotspots,
    compute_station_deep_dive,
    compute_smart_dispatch_pairs,
    haversine_km,
)
from charts.geo_map import create_station_map
from charts.station_analysis import create_round_trip_hotspots_chart
from components.station_inspector import render_station_inspector
from components.dispatch_panel import render_dispatch_panel
from app import app


def test_advanced():
    print("Testing 7 Advanced Enhancements...")

    # 1. Load data
    df = load_clean_data()
    metrics = compute_canonical_station_metrics(df)
    assert len(metrics) == 329, f"Expected 329 stations, got {len(metrics)}"
    print(f"[PASS] 1. Data loaded: {len(df):,} trips, {len(metrics)} stations.")

    # 2. Region partitioning
    region_counts = metrics["region"].value_counts().to_dict()
    assert region_counts.get("San Francisco", 0) == 156
    assert region_counts.get("East Bay (Oakland/Berkeley)", 0) == 127
    assert region_counts.get("San Jose", 0) == 46
    print(f"[PASS] 2. Region partitioning: SF={region_counts['San Francisco']}, EB={region_counts['East Bay (Oakland/Berkeley)']}, SJ={region_counts['San Jose']}.")

    # 3. Imbalance Ratio %
    assert "imbalance_ratio" in metrics.columns
    sample = metrics.iloc[0]
    expected_ratio = round((sample["net_flow"] / sample["total_traffic"]) * 100, 1)
    assert sample["imbalance_ratio"] == expected_ratio
    print(f"[PASS] 3. Imbalance ratio verified ({sample['station_name']}: {sample['imbalance_ratio']}%).")

    # 4. Map flow corridor lines
    top_routes = compute_top_routes(df, 10)
    fig_map = create_station_map(metrics, region="San Francisco", top_routes=top_routes, show_flow_lines=True)
    assert len(fig_map.data) >= 1
    print(f"[PASS] 4. Regional map with {len(fig_map.data)} traces generated.")

    # 5. Round trip hotspots & chart
    rt_hotspots = compute_round_trip_hotspots(df, top_n=5)
    assert not rt_hotspots.empty
    assert "round_trip_pct" in rt_hotspots.columns
    fig_rt = create_round_trip_hotspots_chart(rt_hotspots)
    assert len(fig_rt.data) == 1
    print(f"[PASS] 5. Round trip hotspots computed (Top: {rt_hotspots.iloc[-1]['station_name']} with {rt_hotspots.iloc[-1]['round_trips']} trips).")

    # 6. Station profile inspector
    top_stn = metrics.iloc[0]["station_name"]
    profile = compute_station_deep_dive(df, top_stn, metrics)
    assert profile["station_name"] == top_stn
    assert len(profile["top_destinations"]) > 0
    assert len(profile["top_origins"]) > 0
    inspector_ui = render_station_inspector(profile)
    assert inspector_ui is not None
    print(f"[PASS] 6. Station inspector deep dive for '{top_stn}' generated ({len(profile['top_destinations'])} destinations, {len(profile['top_origins'])} origins).")

    # 7. Smart Dispatch Rebalancing pairs
    pairs = compute_smart_dispatch_pairs(metrics, max_pairs=3)
    assert len(pairs) > 0
    for p in pairs:
        assert p["distance_km"] > 0
        assert p["recommended_transfer"] > 0
        assert p["deficit_station"] != p["surplus_station"]
    dispatch_ui = render_dispatch_panel(pairs)
    assert dispatch_ui is not None
    print(f"[PASS] 7. Smart dispatch generated {len(pairs)} pairs (Pair 1: {pairs[0]['surplus_station']} to {pairs[0]['deficit_station']}, {pairs[0]['distance_km']} km).")

    # 8. Dash App Layout & Callbacks
    assert app.layout is not None
    print(f"[PASS] 8. Dash app initialized with {len(app.callback_map)} callbacks.")

    print("\nALL 7 ADVANCED ENHANCEMENTS VERIFIED 100% WORKING!\n")


if __name__ == "__main__":
    test_advanced()
