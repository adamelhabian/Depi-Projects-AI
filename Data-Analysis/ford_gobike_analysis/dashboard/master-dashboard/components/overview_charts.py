"""
components/overview_charts.py – Executive Overview Visual Analytics
====================================================================
Interactive Plotly visual analytics for the Master Executive Overview:
  1. 24-Hour Diurnal Fleet Volume & Duration Trend (Dual-Axis)
  2. Bay Area Multi-Region Density Mini-Map (Carto-Positron)
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Check mapbox / map trace availability for plotly versions
try:
    _MAP_TRACE = go.Scattermap
    _MAP_LAYOUT_KEY = "map"
except AttributeError:
    _MAP_TRACE = go.Scattermapbox
    _MAP_LAYOUT_KEY = "mapbox"

# Regional Color Palette for Mini-Map
REGION_COLORS = {
    "San Francisco": "#10B981",  # Emerald
    "East Bay": "#0D9488",       # Teal
    "San Jose": "#6366F1",       # Indigo
}


def create_overview_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Build a dual-axis executive trend chart showing:
      - Bar/Area: 24-hour trip volume with commute rush peaks (8 AM & 5 PM)
      - Line: Average trip duration (minutes) across hours
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No trend data available",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
        )
        return fig

    # Format hour labels (e.g. 0 -> "12 AM", 8 -> "8 AM", 17 -> "5 PM")
    def format_hour(h: int) -> str:
        if h == 0:
            return "12 AM"
        elif h < 12:
            return f"{h} AM"
        elif h == 12:
            return "12 PM"
        else:
            return f"{h - 12} PM"

    hour_labels = [format_hour(int(h)) for h in df["hour"]]

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Bar Trace: Trip Volume
    fig.add_trace(
        go.Bar(
            x=hour_labels,
            y=df["trip_count"],
            name="Trip Volume",
            marker=dict(
                color=df["trip_count"],
                colorscale=[
                    [0.0, "rgba(99, 102, 241, 0.4)"],
                    [0.5, "rgba(99, 102, 241, 0.75)"],
                    [1.0, "rgba(79, 70, 229, 0.95)"],
                ],
                line=dict(color="#4338CA", width=1),
                cornerradius=4,
            ),
            hovertemplate="<b>%{x}</b><br>Volume: <b>%{y:,} trips</b><extra></extra>",
        ),
        secondary_y=False,
    )

    # 2. Line Trace: Average Duration
    fig.add_trace(
        go.Scatter(
            x=hour_labels,
            y=df["avg_duration"],
            name="Avg Duration (min)",
            mode="lines+markers",
            line=dict(color="#10B981", width=3, shape="spline"),
            marker=dict(size=6, color="#059669", line=dict(color="#ffffff", width=1.5)),
            hovertemplate="<b>%{x}</b><br>Avg Duration: <b>%{y:.1f} min</b><extra></extra>",
        ),
        secondary_y=True,
    )

    # Executive Layout Styling
    fig.update_layout(
        font=dict(family="Inter, -apple-system, sans-serif", size=11, color="#475569"),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=320,
        margin=dict(l=40, r=40, t=20, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#64748B"),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0F172A",
            font=dict(color="#FFFFFF", size=12),
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor="#E2E8F0",
        tickfont=dict(size=10, color="#64748B"),
    )
    fig.update_yaxes(
        title_text="Trips Volume",
        title_font=dict(size=11, color="#6366F1"),
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="Duration (min)",
        title_font=dict(size=11, color="#10B981"),
        showgrid=False,
        linecolor="#E2E8F0",
        range=[0, max(df["avg_duration"].max() * 1.35, 25)],
        secondary_y=True,
    )

    return fig


def create_overview_minimap(df: pd.DataFrame) -> go.Figure:
    """
    Build an interactive geospatial scatter mini-map showing the 329 stations
    clustered across the Bay Area (San Francisco, East Bay, San Jose).
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No geospatial data available",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
        )
        return fig

    # Scale marker sizes: min 5px, max 16px
    min_trips = df["trips"].min()
    max_trips = df["trips"].max()
    rng = max_trips - min_trips if max_trips != min_trips else 1
    sizes = [round(5 + (t - min_trips) / rng * 11, 1) for t in df["trips"]]

    # Marker colors by region
    colors = [REGION_COLORS.get(r, "#10B981") for r in df["region"]]

    fig = go.Figure(
        _MAP_TRACE(
            lat=df["lat"],
            lon=df["lon"],
            mode="markers",
            marker=dict(
                size=sizes,
                color=colors,
                opacity=0.85,
            ),
            text=df["station_name"],
            customdata=list(zip(df["region"], df["trips"])),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Cluster: <b>%{customdata[0]}</b><br>"
                "Total Departures: <b>%{customdata[1]:,}</b>"
                "<extra></extra>"
            ),
        )
    )

    # Dynamic mapbox layout centered on Greater Bay Area
    map_config = {
        "style": "carto-positron",
        "center": {"lat": 37.65, "lon": -122.25},
        "zoom": 8.8,
    }

    fig.update_layout(
        **{_MAP_LAYOUT_KEY: map_config},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=320,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#0F172A",
            font=dict(color="#FFFFFF", size=12, family="Inter"),
        ),
    )

    return fig
