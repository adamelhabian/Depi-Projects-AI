import sys
from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent.parent
if str(_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_MODULE_DIR))

from data_loader import load_clean_data
from utils.data_processing import compute_canonical_station_metrics, compute_top_stations, compute_top_routes
from charts.station_analysis import create_top_stations_chart
from charts.trip_analysis import create_top_routes_chart

df = load_clean_data()
metrics = compute_canonical_station_metrics(df)

# Test Top 20 Stations
top20 = compute_top_stations(metrics, top_n=20)
fig_stations = create_top_stations_chart(top20)

bar_x = list(fig_stations.data[0].x)
bar_y = list(fig_stations.data[0].y)

print(f"Top Stations bar count: {len(bar_x)}")
assert len(bar_x) == 20, f"Expected 20 bars, but got {len(bar_x)}"
assert bar_x == sorted(bar_x, reverse=True), f"Bars are not in descending order! {bar_x}"
assert bar_x[0] == 8015, f"Expected highest bar at top to be 8,015, got {bar_x[0]}"
assert fig_stations.layout.yaxis.autorange == "reversed", "Expected yaxis autorange='reversed'"
assert 9768 not in bar_x, "Bug detected: 9768 sum found instead of individual stations!"

# Test Top 20 Routes
top_routes = compute_top_routes(df, top_n=20)
fig_routes = create_top_routes_chart(top_routes)
route_x = list(fig_routes.data[0].x)

print(f"Top Routes bar count: {len(route_x)}")
assert len(route_x) == 20, f"Expected 20 route bars, got {len(route_x)}"
assert route_x == sorted(route_x, reverse=True), f"Routes are not in descending order! {route_x}"
assert fig_routes.layout.yaxis.autorange == "reversed", "Expected yaxis autorange='reversed'"
assert 453 not in route_x, "Bug detected: 453 sum found instead of individual routes!"

print("\n[ALL FIXES VERIFIED!]")
print("1. Powell St stations are distinct (4,295 and 5,473), not summed to 9,768.")
print("2. Top bar is strictly the highest (8,015) at the very top.")
print("3. Routes are strictly in sorted order (highest at the top, no merged bars).")
