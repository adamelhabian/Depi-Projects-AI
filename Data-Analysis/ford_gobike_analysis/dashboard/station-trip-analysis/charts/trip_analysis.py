"""
charts/trip_analysis.py – Origin–Destination Corridor Visualizations
=====================================================================
Plotly chart generator for:
  - Top Origin–Destination Corridors (rank-gradient colors, network % labels)
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_BAR
from utils.theme import apply_chart_theme, empty_figure


def _rank_gradient(n_bars: int, dark: str = "#0D9488", light: str = "#CCFBF1") -> list[str]:
    """
    Generate a list of n_bars hex colors from light (lowest rank) to dark (highest rank).
    Data is sorted ascending, so index 0 = lowest rank, index n-1 = highest rank (top bar).
    """
    if n_bars <= 1:
        return [dark]

    def hex_to_rgb(h: str) -> tuple[int, int, int]:
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def rgb_to_hex(r: int, g: int, b: int) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"

    r1, g1, b1 = hex_to_rgb(light)
    r2, g2, b2 = hex_to_rgb(dark)

    colors = []
    for i in range(n_bars):
        t = i / (n_bars - 1)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        colors.append(rgb_to_hex(r, g, b))

    return colors


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

    # Rank-gradient colors: light (bottom) → dark teal (top)
    bar_colors = _rank_gradient(n_bars, dark="#0D9488", light="#CCFBF1")

    custom_data = top_routes[["route", "trip_count", "pct_of_total"]].values

    # Bar text with network share percentage
    bar_texts = [
        f"{tc:,} — {pct:.2f}%"
        for tc, pct in zip(top_routes["trip_count"], top_routes["pct_of_total"])
    ]

    fig = go.Figure(
        go.Bar(
            x=top_routes["trip_count"],
            y=routes,  # Unique route key ensures no bars get merged
            orientation="h",
            marker=dict(
                color=bar_colors,
                line=dict(width=0),
            ),
            customdata=custom_data,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br><br>"
                "Trips: <b>%{x:,}</b><br>"
                "Share of Network: <b>%{customdata[2]:.2f}%</b>"
                "<extra></extra>"
            ),
            text=bar_texts,
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
