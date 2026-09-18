"""
charts/geo_map.py – Geospatial Network & Flow Corridor Map
===========================================================
Interactive Plotly map displaying:
  1. Station nodes (size = total traffic, color = net flow)
  2. Flow Corridor Lines (connects origin & destination hubs on demand)
  3. Dynamic Region Auto-centering (San Francisco, East Bay, San Jose)
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import (
    COLORS,
    MAP_TILE_STYLE,
    REGIONS,
    CHART_HEIGHT_MAP,
)
from utils.theme import empty_figure

try:
    _MAP_TRACE = go.Scattermap
    _MAP_LAYOUT_KEY = "map"
except AttributeError:
    _MAP_TRACE = go.Scattermapbox
    _MAP_LAYOUT_KEY = "mapbox"


def _scale_marker_sizes(traffic_series: pd.Series, min_px: int = 7, max_px: int = 24) -> pd.Series:
    """Scale station traffic proportionally to marker pixel diameters."""
    if traffic_series.empty:
        return traffic_series
    mn = traffic_series.min()
    mx = traffic_series.max()
    if mn == mx:
        return pd.Series([12] * len(traffic_series), index=traffic_series.index)
    return min_px + (traffic_series - mn) / (mx - mn) * (max_px - min_px)


def create_station_map(
    station_metrics: pd.DataFrame,
    region: str = "All",
    top_routes: pd.DataFrame | None = None,
    show_flow_lines: bool = True,
) -> go.Figure:
    """
    Build the Station Traffic, Net Flow & Flow Corridor Map.

    Parameters
    ----------
    station_metrics : pd.DataFrame
        Canonical station metrics table.
    region : str
        Selected region: 'All', 'San Francisco', 'East Bay (Oakland/Berkeley)', or 'San Jose'.
    top_routes : pd.DataFrame, optional
        Top corridors table for plotting transit lines between hubs.
    show_flow_lines : bool
        Whether to render flow corridor lines on the map.

    Returns
    -------
    go.Figure
    """
    if station_metrics.empty:
        return empty_figure("No station data available for the selected filters.", height=CHART_HEIGHT_MAP)

    valid_stations = station_metrics[station_metrics.get("has_valid_coords", True) == True].copy()
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

    # -----------------------------------------------------------------------
    # Layer 1: Transit Flow Lines (Corridor Arcs)
    # -----------------------------------------------------------------------
    if show_flow_lines and top_routes is not None and not top_routes.empty:
        # Build lookup table for station coords
        coord_map = valid_stations.set_index("station_name")[["lat", "lon"]].to_dict("index")

        line_lats = []
        line_lons = []
        for route_str in top_routes["route"].head(12):
            if " → " in route_str:
                origin, dest = route_str.split(" → ", 1)
                if origin in coord_map and dest in coord_map:
                    orig_coords = coord_map[origin]
                    dest_coords = coord_map[dest]
                    line_lats.extend([orig_coords["lat"], dest_coords["lat"], None])
                    line_lons.extend([orig_coords["lon"], dest_coords["lon"], None])

        if line_lats:
            corridor_trace = _MAP_TRACE(
                lat=line_lats,
                lon=line_lons,
                mode="lines",
                line=dict(width=2.5, color=COLORS["accent_teal"]),
                opacity=0.65,
                hoverinfo="none",
                name="Top Corridors",
            )
            fig.add_trace(corridor_trace)

    # -----------------------------------------------------------------------
    # Layer 2: Station Markers
    # -----------------------------------------------------------------------
    marker_sizes = _scale_marker_sizes(valid_stations["total_traffic"])

    hover_texts = [
        (
            f"<b>{row.station_name}</b><br>"
            f"<span style='color:{COLORS['text_muted']};font-size:11px;'>Region: {row.region}</span><br><br>"
            f"Total Traffic: <b>{row.total_traffic:,}</b><br>"
            f"Departures: <b>{row.departures:,}</b><br>"
            f"Arrivals: <b>{row.arrivals:,}</b><br>"
            f"Net Flow: <b>{row.net_flow:+,}</b> (<b>{row.imbalance_ratio:+.1f}%</b>)<br><br>"
            f"<span style='color:{COLORS['accent_dim']};font-size:11px;'>👆 Click station for Deep Dive</span>"
        )
        for row in valid_stations.itertuples()
    ]

    station_trace = _MAP_TRACE(
        lat=valid_stations["lat"],
        lon=valid_stations["lon"],
        mode="markers",
        marker=dict(
            size=marker_sizes,
            color=valid_stations["net_flow"],
            colorscale=[
                [0.0, COLORS["danger"]],      # Outbound pressure (deficit)
                [0.5, "#94A3B8"],             # Balanced
                [1.0, COLORS["success"]],     # Inbound pressure (surplus)
            ],
            colorbar=dict(
                title=dict(
                    text="Net Flow",
                    font=dict(color=COLORS["text_primary"], size=12),
                ),
                thickness=12,
                len=0.55,
                x=0.98,
                xanchor="right",
                y=0.08,
                yanchor="bottom",
                tickfont=dict(color=COLORS["text_secondary"], size=10),
                bgcolor="rgba(255, 255, 255, 0.92)",
                bordercolor=COLORS["border"],
                borderwidth=1,
            ),
            opacity=0.9,
            sizemode="diameter",
        ),
        text=hover_texts,
        customdata=valid_stations["station_name"].values,
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
        paper_bgcolor=COLORS["bg_card"],
        plot_bgcolor=COLORS["bg_card"],
        height=CHART_HEIGHT_MAP,
        margin=dict(r=0, t=0, l=0, b=0),
        showlegend=False,
    )

    return fig
