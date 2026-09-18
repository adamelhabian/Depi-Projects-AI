"""
charts/trip_analysis.py – Origin–Destination Corridor Visualizations
=====================================================================
Plotly chart generator for Top Corridors matching Chart.js aesthetic in station_trip_analysis.html:
  - Teal gradient with rank-opacity scaling
  - Clean borders (#0f766e) and light gridlines (#f1f5f9)
  - Dark hoverlabel card matching Leaflet custom tooltip
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_BAR
from utils.theme import apply_chart_theme, empty_figure


def _clean_short_route(route: str, rank: int, max_len: int = 30) -> str:
    """Format corridor strings cleanly onto a single line."""
    s = str(route).strip()
    s = (
        s.replace("San Francisco ", "SF ")
        .replace("Station", "Stn")
        .replace("BART ", "")
        .replace("Caltrain ", "")
    )

    if " → " in s:
        origin, dest = s.split(" → ", 1)
        o = origin.split("(")[0].strip()
        d = dest.split("(")[0].strip()
        o_short = o[:12].rstrip() + "…" if len(o) > 13 else o
        d_short = d[:12].rstrip() + "…" if len(d) > 13 else d
        return f"{o_short} ➔ {d_short}"

    if len(s) > max_len:
        s = s[: max_len - 1].rstrip() + "…"
    return s


def create_top_routes_chart(top_routes: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart showing the most common origin → destination trips matching station_trip_analysis.html.
    """
    if top_routes.empty:
        return empty_figure("No corridor route data available for the selected filters.", height=CHART_HEIGHT_BAR)

    n_bars = len(top_routes)
    dynamic_height = max(CHART_HEIGHT_BAR, n_bars * 28 + 60)

    routes = top_routes["route"].tolist()

    display_ticks = [
        _clean_short_route(r, rank=n_bars - i)
        for i, r in enumerate(routes)
    ]

    # Teal gradient from HTML reference
    bar_colors = [
        f"rgba(13, 148, 136, {0.45 + (i / max(1, n_bars - 1)) * 0.55:.2f})"
        for i in range(n_bars)
    ]

    custom_data = top_routes[["route", "trip_count", "pct_of_total"]].values

    bar_texts = [
        f"{tc:,} ({pct:.1f}%)"
        for tc, pct in zip(top_routes["trip_count"], top_routes["pct_of_total"])
    ]

    hover_texts = [
        f"<b>Flow Corridor</b><br><br>"
        f"{r}<br>"
        f"Volume: <b>{tc:,} journeys</b> ({pct:.2f}% of network)"
        for r, tc, pct in zip(routes, top_routes["trip_count"], top_routes["pct_of_total"])
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
            textfont=dict(color="#0f172a", size=10, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
        )
    )

    fig = apply_chart_theme(
        fig,
        height=dynamic_height,
        margin=dict(l=10, r=30, t=10, b=30),
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
            categoryorder="array",
            categoryarray=routes,
            tickmode="array",
            tickvals=routes,
            ticktext=display_ticks,
            tickfont=dict(color="#334155", size=11, family="Inter"),
        ),
        bargap=0.25,
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig
