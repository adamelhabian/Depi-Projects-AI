"""
charts/trip_analysis.py – Origin–Destination Corridor Visualizations
=====================================================================
Plotly chart generator for:
  - Top Origin–Destination Corridors (Horizontal bar chart)

Key UI & Readability Fixes:
  - Clean single-line corridor labels with rank prefix ("1. ", "2. ") so labels NEVER overlap.
  - Passes unique route strings to `y` to avoid Plotly category-merging bugs.
  - Dynamic height ensures 15 and 20 bars get comfortable vertical spacing.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_BAR
from utils.theme import apply_chart_theme, empty_figure


def _clean_short_route(route: str, rank: int, max_len: int = 34) -> str:
    """Format corridor strings cleanly onto a single line with rank prefix."""
    s = str(route).strip()
    s = (
        s.replace("San Francisco ", "SF ")
        .replace("Station", "Stn")
        .replace("BART ", "")
        .replace("Caltrain ", "")
    )

    if " → " in s:
        origin, dest = s.split(" → ", 1)
        o = origin[:13].rstrip() + "…" if len(origin) > 14 else origin.strip()
        d = dest[:13].rstrip() + "…" if len(dest) > 14 else dest.strip()
        return f"{rank}. {o} → {d}"

    if len(s) > max_len:
        s = s[: max_len - 1].rstrip() + "…"
    return f"{rank}. {s}"


def create_top_routes_chart(top_routes: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart showing the most common origin → destination trips.

    Parameters
    ----------
    top_routes : pd.DataFrame
        Output of compute_top_routes(); sorted ascending by trip_count.
        Required columns: route, trip_count, pct_of_total.

    Returns
    -------
    go.Figure
    """
    if top_routes.empty:
        return empty_figure("No corridor route data available for the selected filters.", height=CHART_HEIGHT_BAR)

    n_bars = len(top_routes)
    dynamic_height = max(CHART_HEIGHT_BAR, n_bars * 26 + 80)

    routes = top_routes["route"].tolist()

    # Generate single-line labels with rank prefix (1 = highest trips at top)
    display_ticks = [
        _clean_short_route(r, rank=n_bars - i)
        for i, r in enumerate(routes)
    ]

    custom_data = top_routes[["route", "trip_count", "pct_of_total"]].values

    fig = go.Figure(
        go.Bar(
            x=top_routes["trip_count"],
            y=routes,  # Unique route key ensures no bars get merged
            orientation="h",
            marker=dict(
                color=top_routes["trip_count"],
                colorscale=[
                    [0.0, "#34D399"],   # Mint Green
                    [1.0, "#0D9488"],   # Teal
                ],
                showscale=False,
                line=dict(width=0),
            ),
            customdata=custom_data,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br><br>"
                "Trips: <b>%{x:,}</b><br>"
                "Share of Network: <b>%{customdata[2]:.2f}%</b>"
                "<extra></extra>"
            ),
            text=top_routes["trip_count"].apply(lambda v: f"{v:,}"),
            textposition="auto",
            textfont=dict(color=COLORS["text_primary"], size=10),
        )
    )

    fig = apply_chart_theme(
        fig,
        height=dynamic_height,
        margin=dict(l=10, r=40, t=20, b=30),
    )

    fig.update_layout(
        xaxis=dict(
            title="Number of Trips",
            tickformat=",",
            showgrid=True,
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            categoryorder="array",
            categoryarray=routes,
            tickmode="array",
            tickvals=routes,
            ticktext=display_ticks,
            tickfont=dict(color=COLORS["text_secondary"], size=11),
        ),
        bargap=0.25,
    )

    return fig
