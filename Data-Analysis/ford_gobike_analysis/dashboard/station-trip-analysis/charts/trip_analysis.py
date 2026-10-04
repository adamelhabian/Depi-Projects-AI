"""
charts/trip_analysis.py – Origin–Destination Corridor Visualizations
=====================================================================
Plotly chart generator for Top Corridors matching Chart.js aesthetic in station_trip_analysis.html:
  - Strictly sorted from highest volume (top) to lowest volume (bottom)
  - Teal gradient with rank-opacity scaling (1.0 down to 0.45)
  - Dark hoverlabel card matching Leaflet custom tooltip
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_BAR
from utils.theme import apply_chart_theme, empty_figure


def _clean_two_line_route(route: str) -> str:
    """Format corridor strings cleanly onto two lines (Origin / -> Destination) without ellipses truncation."""
    s = str(route).strip()
    s = (
        s.replace("San Francisco ", "SF ")
        .replace("Station", "Stn")
        .replace("BART Station", "BART")
        .replace("BART ", "")
        .replace("Caltrain Station", "Caltrain")
    )
    if " → " in s:
        origin, dest = s.split(" → ", 1)
        return f"{origin.strip()}<br>→ {dest.strip()}"
    return s


def create_top_routes_chart(top_routes: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart showing origin → destination trips strictly ordered from highest (top) to lowest.
    Corridor labels are formatted as two lines with full names in hover and rank + trips on bars.
    """
    if top_routes.empty:
        return empty_figure("No corridor route data available for the selected filters.", height=CHART_HEIGHT_BAR)

    n_bars = len(top_routes)
    dynamic_height = max(380, n_bars * 38 + 60)

    routes = top_routes["route"].tolist()

    display_ticks = [
        _clean_two_line_route(r)
        for r in routes
    ]

    # Teal gradient from 1.0 (top rank) down to 0.45
    bar_colors = [
        f"rgba(13, 148, 136, {1.0 - (i / max(1, n_bars - 1)) * 0.55:.2f})"
        for i in range(n_bars)
    ]

    custom_data = top_routes[["route", "trip_count", "pct_of_total"]].values

    # Value labels on bars: Rank + Trips (e.g. "#1  327")
    bar_texts = [
        f"#{i + 1}  {tc:,}"
        for i, tc in enumerate(top_routes["trip_count"])
    ]

    hover_texts = [
        f"<b>Corridor Rank #{i + 1}</b><br><br>"
        f"<b>{r}</b><br>"
        f"Volume: <b>{tc:,} journeys</b> ({pct:.2f}% of network)"
        for i, (r, tc, pct) in enumerate(zip(routes, top_routes["trip_count"], top_routes["pct_of_total"]))
    ]

    fig = go.Figure(
        go.Bar(
            x=top_routes["trip_count"],
            y=routes,
            orientation="h",
            marker=dict(
                color=bar_colors,
                line=dict(color="#0f766e", width=1),
            ),
            customdata=custom_data,
            text=bar_texts,
            textposition="auto",
            textfont=dict(color="#0f172a", size=10.5, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
        )
    )

    fig = apply_chart_theme(
        fig,
        height=dynamic_height,
        margin=dict(l=190, r=30, t=10, b=30),
    )

    fig.update_layout(
        xaxis=dict(
            title="",
            tickformat=",",
            showgrid=True,
            gridcolor="#f1f5f9",
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            automargin=True,
            categoryorder="array",
            categoryarray=routes,
            tickmode="array",
            tickvals=routes,
            ticktext=display_ticks,
            tickfont=dict(color="#334155", size=10.5, family="Inter"),
            autorange="reversed",  # Highest volume corridor at top
        ),
        bargap=0.22,
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig
