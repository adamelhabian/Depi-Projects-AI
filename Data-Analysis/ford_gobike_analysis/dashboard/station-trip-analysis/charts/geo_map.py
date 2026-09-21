"""
charts/geo_map.py – Geospatial Network & Flow Corridor Map
===========================================================
Interactive Plotly map displaying:
  1. Station nodes (size = total traffic, color = net flow)
  2. Flow Corridor Lines (variable thickness by trip volume, per-corridor hover)
  3. Dynamic Region Auto-centering (San Francisco, East Bay, San Jose)
  4. Fixed in-bounds legend explaining marker size vs color
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import pandas as pd

from config import (
    COLORS,
    MAP_TILE_STYLE,
    REGIONS,
    CHART_HEIGHT_MAP,
)
from utils.theme import empty_figure, COLORSCALE_NET_FLOW

try:
    _MAP_TRACE = go.Scattermap
    _MAP_LAYOUT_KEY = "map"
except AttributeError:
    _MAP_TRACE = go.Scattermapbox
    _MAP_LAYOUT_KEY = "mapbox"


def _scale_marker_sizes(traffic_series: pd.Series, min_px: float = 6.0, max_px: float = 22.0) -> pd.Series:
    """Scale station traffic proportionally using square root to marker pixel diameters to avoid massive overlap."""
    if traffic_series.empty:
        return traffic_series
    sqrt_traffic = np.sqrt(traffic_series.clip(lower=0))
    mn = sqrt_traffic.min()
    mx = sqrt_traffic.max()
    if mn == mx:
        return pd.Series([10.0] * len(traffic_series), index=traffic_series.index)
    return min_px + (sqrt_traffic - mn) / (mx - mn) * (max_px - min_px)


def _scale_line_width(trip_count: int, min_count: int, max_count: int,
                      min_w: float = 1.5, max_w: float = 6.0) -> float:
    """Scale corridor line width proportionally to trip volume."""
    if max_count == min_count:
        return (min_w + max_w) / 2
    return min_w + (trip_count - min_count) / (max_count - min_count) * (max_w - min_w)


def create_station_map(
    station_metrics: pd.DataFrame,
    region: str = "All",
    top_routes: pd.DataFrame | None = None,
    show_flow_lines: bool = True,
    top_dest_map: dict[str, str] | None = None,
) -> go.Figure:
    """
    Build the Station Traffic, Net Flow & Flow Corridor Map.

    Parameters
    ----------
    station_metrics : pd.DataFrame
        Canonical station metrics table.
    region : str
        Selected region.
    top_routes : pd.DataFrame, optional
        Top corridors table for plotting transit lines between hubs.
    show_flow_lines : bool
        Whether to render flow corridor lines on the map.
    top_dest_map : dict[str, str], optional
        Mapping of station_name -> its #1 destination station name.

    Returns
    -------
    go.Figure
    """
    if station_metrics.empty:
        return empty_figure("No station data available for the selected filters.", height=CHART_HEIGHT_MAP)

    if "has_valid_coords" in station_metrics.columns:
        valid_stations = station_metrics[station_metrics["has_valid_coords"] == True].copy()
    else:
        valid_stations = station_metrics.copy()
    valid_stations = valid_stations.dropna(subset=["lat", "lon"])

    # Filter by region if requested
    if region and region != "All":
        valid_stations = valid_stations[valid_stations["region"] == region]

    if valid_stations.empty:
        return empty_figure(
            f"No active stations found in {region} for the selected filters.",
            height=CHART_HEIGHT_MAP,
        )

    fig = go.Figure()
    dest_lookup = top_dest_map or {}

    # -----------------------------------------------------------------------
    # Layer 1: Transit Flow Lines (Individual Corridor Traces with Variable Width)
    # -----------------------------------------------------------------------
    if show_flow_lines and top_routes is not None and not top_routes.empty:
        coord_map = valid_stations.set_index("station_name")[["lat", "lon"]].to_dict("index")

        # Determine trip count range for width scaling
        valid_corridor_rows = []
        for _, row in top_routes.head(12).iterrows():
            route_str = row["route"]
            if " → " in route_str:
                origin, dest = route_str.split(" → ", 1)
                if origin in coord_map and dest in coord_map:
                    valid_corridor_rows.append(row)

        if valid_corridor_rows:
            counts = [r["trip_count"] for r in valid_corridor_rows]
            min_count = min(counts)
            max_count = max(counts)

            for row in valid_corridor_rows:
                route_str = row["route"]
                trip_count = int(row["trip_count"])
                origin, dest = route_str.split(" → ", 1)
                orig_c = coord_map[origin]
                dest_c = coord_map[dest]

                line_w = _scale_line_width(trip_count, min_count, max_count)

                corridor_trace = _MAP_TRACE(
                    lat=[orig_c["lat"], dest_c["lat"]],
                    lon=[orig_c["lon"], dest_c["lon"]],
                    mode="lines",
                    line=dict(width=line_w, color=COLORS["accent_teal"]),
                    opacity=0.7,
                    text=f"<b>{origin}</b> → <b>{dest}</b><br>Trips: <b>{trip_count:,}</b>",
                    customdata=[[origin], [dest]],
                    hoverinfo="text",
                    name="",
                    showlegend=False,
                )
                fig.add_trace(corridor_trace)

    # -----------------------------------------------------------------------
    # Layer 2: Station Markers
    # -----------------------------------------------------------------------
    # Sort stations ascending by total traffic so large markers are plotted behind small ones
    valid_stations = valid_stations.sort_values("total_traffic", ascending=True).reset_index(drop=True)

    marker_sizes = _scale_marker_sizes(valid_stations["total_traffic"])

    hover_texts = []
    for row in valid_stations.itertuples():
        top_dest_line = ""
        dest_name = dest_lookup.get(row.station_name)
        if dest_name:
            top_dest_line = (
                f"Top Destination → <b>{dest_name}</b><br><br>"
            )

        hover_texts.append(
            f"<b>{row.station_name}</b><br>"
            f"<span style='color:{COLORS['text_muted']};font-size:11px;'>Region: {row.region}</span><br><br>"
            f"Total Traffic: <b>{row.total_traffic:,}</b><br>"
            f"Net Flow: <b>{row.net_flow:+,}</b> (<b>{row.imbalance_ratio:+.1f}%</b>)<br>"
            f"{top_dest_line}"
            f"<span style='color:{COLORS['accent_dim']};font-size:11px;'>Click for Deep Dive</span>"
        )

    max_flow = max(float(valid_stations["net_flow"].abs().max()), 1.0)

    station_trace = _MAP_TRACE(
        lat=valid_stations["lat"],
        lon=valid_stations["lon"],
        mode="markers",
        marker=dict(
            size=marker_sizes,
            color=valid_stations["net_flow"],
            colorscale=COLORSCALE_NET_FLOW,
            cmin=-max_flow,
            cmax=max_flow,
            cauto=False,
            showscale=False,
            opacity=0.78,
            sizemode="diameter",
        ),
        text=hover_texts,
        customdata=[[s] for s in valid_stations["station_name"]],
        hoverinfo="text",
        name="Stations",
    )
    fig.add_trace(station_trace)

    # -----------------------------------------------------------------------
    # Dynamic Map Viewport Settings (Region Centering & Zoom)
    # -----------------------------------------------------------------------
    region_info = REGIONS.get(region, REGIONS["All"])
    map_dict = {
        "style": MAP_TILE_STYLE,
        "center": region_info["center"],
        "zoom": region_info["zoom"],
    }

    fig.update_layout(
        **{_MAP_LAYOUT_KEY: map_dict},
        clickmode="event+select",
        paper_bgcolor=COLORS["bg_card"],
        plot_bgcolor=COLORS["bg_card"],
        height=CHART_HEIGHT_MAP,
        margin=dict(r=0, t=0, l=0, b=0),
        showlegend=False,
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=12, family="Inter"),
        ),
    )

    return fig
