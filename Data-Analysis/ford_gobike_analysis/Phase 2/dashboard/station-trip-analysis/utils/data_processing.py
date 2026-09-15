"""
utils/data_processing.py – Analytical Engine (Station & Trip Metrics)
=====================================================================
Pure analytical computation module without Plotly or Dash dependencies.

Features implemented:
  1. Station normalization & Route generation
  2. Canonical station identity (no duplicate station rows)
  3. Regional clustering (San Francisco, East Bay, San Jose)
  4. Station Flow Imbalance & Turnover Ratio (%)
  5. Leisure Round-trip Hotspot analysis
  6. Station Profile Inspector queries (Top Origins & Destinations)
  7. Smart Rebalancing Dispatch pairs (Haversine spatial matching)
"""

from __future__ import annotations

import math
import pandas as pd
from config import VALID_LAT_RANGE, VALID_LON_RANGE


# ---------------------------------------------------------------------------
# 1. Normalization & Route Generation
# ---------------------------------------------------------------------------

def normalize_station_name(series: pd.Series) -> pd.Series:
    """Normalize station names consistently without converting NaN to string literals."""
    if series.empty:
        return series

    cleaned = series.astype(str).str.strip()
    invalid_mask = (
        series.isna()
        | (cleaned == "")
        | cleaned.str.lower().isin({"nan", "none", "null", "undefined"})
    )
    cleaned = cleaned.mask(invalid_mask, pd.NA)
    return cleaned


def generate_routes(df: pd.DataFrame) -> pd.Series:
    """Generate clean origin → destination route strings."""
    if df.empty or "start_station_name" not in df.columns or "end_station_name" not in df.columns:
        return pd.Series(dtype="object")

    starts = df["start_station_name"]
    ends = df["end_station_name"]
    valid_mask = starts.notna() & ends.notna()

    routes = pd.Series(pd.NA, index=df.index, dtype="object")
    routes[valid_mask] = starts[valid_mask] + " → " + ends[valid_mask]
    return routes


def assign_station_region(lat: float, lon: float) -> str:
    """
    Classify station coordinates into one of the three Bay Area bicycle sub-networks:
      - San Francisco
      - East Bay (Oakland/Berkeley)
      - San Jose
    """
    if pd.isna(lat) or pd.isna(lon):
        return "Unknown"
    if lat > 37.7 and lon < -122.35:
        return "San Francisco"
    elif lat > 37.75 and lon >= -122.35:
        return "East Bay (Oakland/Berkeley)"
    elif lat < 37.45:
        return "San Jose"
    return "San Francisco"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two GPS coordinates in kilometers."""
    radius = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return radius * c


# ---------------------------------------------------------------------------
# 2. Canonical Station Aggregation
# ---------------------------------------------------------------------------

def compute_canonical_station_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build canonical station-level summary table based strictly on station name.

    Calculates:
      - Total Traffic = Departures + Arrivals
      - Net Flow = Arrivals - Departures
      - Imbalance Ratio (%) = (Net Flow / Total Traffic) * 100
      - Geographic cluster (Region)
    """
    metric_cols = [
        "station_name", "departures", "arrivals",
        "total_traffic", "net_flow", "imbalance_ratio",
        "lat", "lon", "region", "has_valid_coords"
    ]
    if df.empty:
        return pd.DataFrame(columns=metric_cols)

    # 1. Aggregate departures
    valid_starts = df[df["start_station_name"].notna()]
    starts = (
        valid_starts
        .groupby("start_station_name", observed=True)
        .size()
        .reset_index(name="departures")
        .rename(columns={"start_station_name": "station_name"})
    )

    # 2. Aggregate arrivals
    valid_ends = df[df["end_station_name"].notna()]
    ends = (
        valid_ends
        .groupby("end_station_name", observed=True)
        .size()
        .reset_index(name="arrivals")
        .rename(columns={"end_station_name": "station_name"})
    )

    # 3. Outer merge on station name
    stations = pd.merge(starts, ends, on="station_name", how="outer")
    stations["departures"] = stations["departures"].fillna(0).astype(int)
    stations["arrivals"] = stations["arrivals"].fillna(0).astype(int)
    stations["total_traffic"] = stations["departures"] + stations["arrivals"]
    stations["net_flow"] = stations["arrivals"] - stations["departures"]

    # Imbalance / Turnover Ratio (%)
    stations["imbalance_ratio"] = (
        (stations["net_flow"] / stations["total_traffic"].replace(0, 1)) * 100
    ).round(1)

    # 4. Attach representative coordinates (median)
    start_coords = pd.DataFrame(columns=["station_name", "lat", "lon"])
    if {"start_station_latitude", "start_station_longitude"}.issubset(df.columns):
        start_coords = (
            valid_starts
            .groupby("start_station_name", observed=True)
            [["start_station_latitude", "start_station_longitude"]]
            .median()
            .reset_index()
            .rename(columns={
                "start_station_name": "station_name",
                "start_station_latitude": "lat",
                "start_station_longitude": "lon",
            })
        )

    end_coords = pd.DataFrame(columns=["station_name", "lat", "lon"])
    if {"end_station_latitude", "end_station_longitude"}.issubset(df.columns):
        end_coords = (
            valid_ends
            .groupby("end_station_name", observed=True)
            [["end_station_latitude", "end_station_longitude"]]
            .median()
            .reset_index()
            .rename(columns={
                "end_station_name": "station_name",
                "end_station_latitude": "lat",
                "end_station_longitude": "lon",
            })
        )

    coords = pd.merge(start_coords, end_coords, on="station_name", how="outer", suffixes=("_start", "_end"))
    if not coords.empty:
        coords["lat"] = coords["lat_start"].combine_first(coords["lat_end"])
        coords["lon"] = coords["lon_start"].combine_first(coords["lon_end"])
        coords = coords[["station_name", "lat", "lon"]]
        stations = pd.merge(stations, coords, on="station_name", how="left")
    else:
        stations["lat"] = pd.NA
        stations["lon"] = pd.NA

    # 5. Coordinate validity and region tagging
    lat_valid = stations["lat"].between(VALID_LAT_RANGE[0], VALID_LAT_RANGE[1], inclusive="both")
    lon_valid = stations["lon"].between(VALID_LON_RANGE[0], VALID_LON_RANGE[1], inclusive="both")
    stations["has_valid_coords"] = lat_valid & lon_valid & stations["lat"].notna() & stations["lon"].notna()

    stations["region"] = [
        assign_station_region(r.lat, r.lon) for r in stations.itertuples()
    ]

    return stations.sort_values("total_traffic", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. Top-N Rankings & Advanced Subsets
# ---------------------------------------------------------------------------

def compute_top_stations(station_metrics: pd.DataFrame, top_n: int) -> pd.DataFrame:
    """Select Top N stations ranked by total traffic (sorted ascending for horizontal bar)."""
    if station_metrics.empty:
        return station_metrics

    n = max(1, min(top_n, len(station_metrics)))
    return (
        station_metrics
        .nlargest(n, "total_traffic")
        .sort_values("total_traffic", ascending=True)
        .reset_index(drop=True)
    )


def compute_top_routes(df: pd.DataFrame, top_n: int) -> pd.DataFrame:
    """Analyze top origin → destination corridors."""
    cols = ["route", "trip_count", "pct_of_total"]
    if df.empty or "route" not in df.columns:
        return pd.DataFrame(columns=cols)

    valid_routes = df["route"].dropna()
    if valid_routes.empty:
        return pd.DataFrame(columns=cols)

    total_network_trips = len(valid_routes)
    n = max(1, min(top_n, valid_routes.nunique()))

    route_counts = valid_routes.value_counts().nlargest(n).reset_index()
    route_counts.columns = ["route", "trip_count"]
    route_counts["pct_of_total"] = (route_counts["trip_count"] / total_network_trips * 100).round(2)

    return route_counts.sort_values("trip_count", ascending=True).reset_index(drop=True)


def compute_flow_imbalance(station_metrics: pd.DataFrame, top_n: int) -> pd.DataFrame:
    """
    Analyze station flow imbalance (strictly net_flow < 0 for deficit, > 0 for surplus).
    """
    cols = ["station_name", "departures", "arrivals", "total_traffic", "net_flow", "imbalance_ratio", "imbalance_type"]
    if station_metrics.empty or "net_flow" not in station_metrics.columns:
        return pd.DataFrame(columns=cols)

    n_deficit = max(1, top_n // 2)
    n_surplus = max(1, top_n - n_deficit)

    neg_stations = station_metrics[station_metrics["net_flow"] < 0]
    deficit = neg_stations.nsmallest(min(n_deficit, len(neg_stations)), "net_flow").copy()
    if not deficit.empty:
        deficit["imbalance_type"] = "Outbound Pressure"

    pos_stations = station_metrics[station_metrics["net_flow"] > 0]
    surplus = pos_stations.nlargest(min(n_surplus, len(pos_stations)), "net_flow").copy()
    if not surplus.empty:
        surplus["imbalance_type"] = "Inbound Pressure"

    combined = pd.concat([deficit, surplus], ignore_index=True)
    if combined.empty:
        return pd.DataFrame(columns=cols)

    return (
        combined
        .drop_duplicates(subset=["station_name"])
        .sort_values("net_flow", ascending=True)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 4. Feature 5: Leisure & Tourism Hotspots (Round-Trip Analysis)
# ---------------------------------------------------------------------------

def compute_round_trip_hotspots(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Identify stations with the highest concentration of round-trip journeys
    (where start_station == end_station), indicative of recreational and tourist activity.
    """
    cols = ["station_name", "round_trips", "total_departures", "round_trip_pct"]
    if df.empty or "start_station_name" not in df.columns or "end_station_name" not in df.columns:
        return pd.DataFrame(columns=cols)

    # Filter round trips
    round_trips = df[df["start_station_name"] == df["end_station_name"]]
    if round_trips.empty:
        return pd.DataFrame(columns=cols)

    rt_counts = round_trips["start_station_name"].value_counts().reset_index()
    rt_counts.columns = ["station_name", "round_trips"]

    # Calculate station departures
    dep_counts = df["start_station_name"].value_counts().reset_index()
    dep_counts.columns = ["station_name", "total_departures"]

    merged = pd.merge(rt_counts, dep_counts, on="station_name", how="inner")
    merged["round_trip_pct"] = (
        (merged["round_trips"] / merged["total_departures"]) * 100
    ).round(1)

    # Return top N stations sorted ascending for horizontal bar chart
    return (
        merged.nlargest(top_n, "round_trips")
        .sort_values("round_trips", ascending=True)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 5. Feature 1: Station Profile Deep-Dive (Inspector)
# ---------------------------------------------------------------------------

def compute_station_deep_dive(
    df: pd.DataFrame,
    station_name: str,
    station_metrics: pd.DataFrame,
) -> dict:
    """
    Extract comprehensive station profile for drill-down analysis upon clicking.
    """
    empty_result = {
        "station_name": station_name or "None Selected",
        "total_traffic": 0,
        "departures": 0,
        "arrivals": 0,
        "net_flow": 0,
        "imbalance_ratio": 0.0,
        "region": "Unknown",
        "round_trip_count": 0,
        "round_trip_pct": 0.0,
        "top_destinations": [],
        "top_origins": [],
    }

    if df.empty or not station_name:
        return empty_result

    # 1. Base metrics
    match = station_metrics[station_metrics["station_name"] == station_name]
    if not match.empty:
        row = match.iloc[0]
        empty_result.update({
            "station_name": station_name,
            "total_traffic": int(row["total_traffic"]),
            "departures": int(row["departures"]),
            "arrivals": int(row["arrivals"]),
            "net_flow": int(row["net_flow"]),
            "imbalance_ratio": float(row.get("imbalance_ratio", 0.0)),
            "region": str(row.get("region", "Unknown")),
        })

    # 2. Top Destinations (trips starting at station_name)
    trips_from = df[df["start_station_name"] == station_name]
    if not trips_from.empty:
        top_dests = (
            trips_from[trips_from["end_station_name"] != station_name]
            ["end_station_name"]
            .value_counts()
            .head(5)
            .to_dict()
        )
        empty_result["top_destinations"] = [
            {"station": k, "count": v} for k, v in top_dests.items()
        ]

        # Round trip stats
        rts = len(trips_from[trips_from["end_station_name"] == station_name])
        empty_result["round_trip_count"] = rts
        if len(trips_from) > 0:
            empty_result["round_trip_pct"] = round((rts / len(trips_from)) * 100, 1)

    # 3. Top Origins (trips ending at station_name)
    trips_to = df[df["end_station_name"] == station_name]
    if not trips_to.empty:
        top_origs = (
            trips_to[trips_to["start_station_name"] != station_name]
            ["start_station_name"]
            .value_counts()
            .head(5)
            .to_dict()
        )
        empty_result["top_origins"] = [
            {"station": k, "count": v} for k, v in top_origs.items()
        ]

    return empty_result


# ---------------------------------------------------------------------------
# 6. Feature 6: Smart Rebalancing Dispatch Pairs
# ---------------------------------------------------------------------------

def compute_smart_dispatch_pairs(
    station_metrics: pd.DataFrame,
    max_pairs: int = 3,
) -> list[dict]:
    """
    Prescriptive dispatch algorithm:
    Matches top deficit stations with their closest high-surplus neighbor in the same region.
    """
    if station_metrics.empty or len(station_metrics) < 2:
        return []

    # Valid stations with coords
    valid = station_metrics[station_metrics["has_valid_coords"] == True].copy()
    deficits = valid[valid["net_flow"] < -100].sort_values("net_flow").head(8)
    surpluses = valid[valid["net_flow"] > 100].sort_values("net_flow", ascending=False).head(12)

    if deficits.empty or surpluses.empty:
        return []

    pairs = []
    used_surpluses = set()

    for def_row in deficits.itertuples():
        if len(pairs) >= max_pairs:
            break

        # Find closest surplus in the same region
        same_region_surplus = surpluses[
            (surpluses["region"] == def_row.region) & (~surpluses["station_name"].isin(used_surpluses))
        ]

        if same_region_surplus.empty:
            continue

        # Calculate distances
        candidates = []
        for sur_row in same_region_surplus.itertuples():
            dist = haversine_km(def_row.lat, def_row.lon, sur_row.lat, sur_row.lon)
            candidates.append((dist, sur_row))

        candidates.sort(key=lambda x: x[0])
        best_dist, best_sur = candidates[0]

        used_surpluses.add(best_sur.station_name)
        recommended_transfer = min(abs(def_row.net_flow) // 2, best_sur.net_flow // 2)

        pairs.append({
            "region": def_row.region,
            "deficit_station": def_row.station_name,
            "deficit_amount": abs(def_row.net_flow),
            "surplus_station": best_sur.station_name,
            "surplus_amount": best_sur.net_flow,
            "distance_km": round(best_dist, 2),
            "distance_meters": int(best_dist * 1000),
            "recommended_transfer": int(recommended_transfer),
        })

    return pairs


def compute_active_stations_count(df: pd.DataFrame) -> int:
    """Calculate total active stations (union of valid origins and destinations)."""
    if df.empty:
        return 0
    starts = set(df["start_station_name"].dropna().unique()) if "start_station_name" in df.columns else set()
    ends = set(df["end_station_name"].dropna().unique()) if "end_station_name" in df.columns else set()
    return len(starts | ends)
