"""
charts/station_analysis.py – Popular Stations & Flow Imbalance Visualizations
=============================================================================
Plotly chart generators styled with Chart.js-like Tailwind aesthetic matching station_trip_analysis.html:
  1. Top Stations by Total Traffic (emerald rank-opacity gradient, dark hoverlabel)
  2. Station Flow Imbalance (pink deficit vs emerald surplus, dark slate zero line)
  3. Leisure & Tourism Hotspots (purple/violet gradient, percentage axis)
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_BAR, CHART_HEIGHT_IMBALANCE, CHART_HEIGHT_LEISURE
from utils.theme import apply_chart_theme, empty_figure


def _clean_short_station(name: str, max_chars: int = 24) -> str:
    """Clean and abbreviate station names for single-line display."""
    s = str(name).strip()
    s = s.split("(")[0].strip()
    s = (
        s.replace("San Francisco ", "SF ")
        .replace("Station", "Stn")
        .replace("BART ", "")
        .replace("Caltrain ", "")
    )
    if len(s) > max_chars:
        s = s[: max_chars - 1].rstrip() + "…"
    return s


# ---------------------------------------------------------------------------
# 1. Top Stations by Total Traffic (Emerald Rank-Opacity Gradient)
# ---------------------------------------------------------------------------

def create_top_stations_chart(
    top_stations: pd.DataFrame,
    total_network_traffic: int = 0,
) -> go.Figure:
    """
    Horizontal bar chart styled like Chart.js in station_trip_analysis.html.
    """
    if top_stations.empty:
        return empty_figure("No station data available for the selected filters.", height=CHART_HEIGHT_BAR)

    n_bars = len(top_stations)
    dynamic_height = max(CHART_HEIGHT_BAR, n_bars * 28 + 60)

    station_names = top_stations["station_name"].tolist()

    # Generate labels matching reference
    display_ticks = [
        _clean_short_station(name, 22)
        for name in station_names
    ]

    # Rank-opacity emerald gradient: bottom bar (lowest rank) is 0.45, top bar is 1.0
    bar_colors = [
        f"rgba(16, 185, 129, {0.40 + (i / max(1, n_bars - 1)) * 0.60:.2f})"
        for i in range(n_bars)
    ]

    custom_data = top_stations[
        ["station_name", "departures", "arrivals", "net_flow"]
    ].values

    if total_network_traffic > 0:
        shares = [
            f"{v / total_network_traffic * 100:.1f}%"
            for v in top_stations["total_traffic"]
        ]
        bar_texts = [
            f"{v:,} ({s})"
            for v, s in zip(top_stations["total_traffic"], shares)
        ]
    else:
        shares = ["0.0%"] * n_bars
        bar_texts = top_stations["total_traffic"].apply(lambda v: f"{v:,}").tolist()

    hover_texts = [
        f"<b>{name}</b><br><br>"
        f"Total Volume: <b>{v:,} trips</b> ({s} of filtered network)<br>"
        f"Departures: <b>{d:,}</b> | Arrivals: <b>{a:,}</b><br>"
        f"Net Flow: <b>{nf:+,}</b>"
        for name, v, s, d, a, nf in zip(
            station_names,
            top_stations["total_traffic"],
            shares,
            top_stations["departures"],
            top_stations["arrivals"],
            top_stations["net_flow"],
        )
    ]

    fig = go.Figure(
        go.Bar(
            x=top_stations["total_traffic"],
            y=station_names,
            orientation="h",
            marker=dict(
                color=bar_colors,
                line=dict(color="#059669", width=1),
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
            categoryarray=station_names,
            tickmode="array",
            tickvals=station_names,
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


# ---------------------------------------------------------------------------
# 2. Station Flow Imbalance (Pink Deficit vs Emerald Surplus)
# ---------------------------------------------------------------------------

def create_flow_imbalance_chart(flow_imbalance: pd.DataFrame) -> go.Figure:
    """
    Diverging horizontal bar chart displaying network flow imbalance matching station_trip_analysis.html.
    """
    if flow_imbalance.empty:
        return empty_figure("No flow imbalance data available for the selected filters.", height=CHART_HEIGHT_IMBALANCE)

    n_bars = len(flow_imbalance)
    dynamic_height = max(CHART_HEIGHT_IMBALANCE, n_bars * 28 + 60)

    station_names = flow_imbalance["station_name"].tolist()
    display_ticks = [_clean_short_station(name, 22) for name in station_names]

    bar_colors = [
        "rgba(244, 63, 94, 0.85)" if val < 0 else "rgba(16, 185, 129, 0.85)"
        for val in flow_imbalance["net_flow"]
    ]
    border_colors = [
        "#e11d48" if val < 0 else "#059669"
        for val in flow_imbalance["net_flow"]
    ]

    custom_data = flow_imbalance[
        ["station_name", "departures", "arrivals", "imbalance_type"]
    ].values

    hover_texts = [
        f"<b>{name}</b><br><br>"
        f"Status: <b>{cat}</b><br>"
        f"Net Flow: <b>{nf:+,}</b> ({'Surplus: dock overflow risk' if nf >= 0 else 'Deficit: dock depletion risk'})<br>"
        f"Departures: <b>{d:,}</b> | Arrivals: <b>{a:,}</b>"
        for name, d, a, cat, nf in zip(
            station_names,
            flow_imbalance["departures"],
            flow_imbalance["arrivals"],
            flow_imbalance["imbalance_type"],
            flow_imbalance["net_flow"],
        )
    ]

    fig = go.Figure(
        go.Bar(
            x=flow_imbalance["net_flow"],
            y=station_names,
            orientation="h",
            marker=dict(
                color=bar_colors,
                line=dict(color=border_colors, width=1),
            ),
            customdata=custom_data,
            text=flow_imbalance["net_flow"].apply(lambda v: f"{v:+,}"),
            textposition="auto",
            textfont=dict(color="#0f172a", size=10, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
        )
    )

    # Vertical zero baseline matching HTML reference
    fig.add_vline(
        x=0,
        line_width=2,
        line_color="#475569",
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
            zeroline=False,
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            categoryorder="array",
            categoryarray=station_names,
            tickmode="array",
            tickvals=station_names,
            ticktext=display_ticks,
            tickfont=dict(color="#334155", size=11, family="Inter"),
        ),
        bargap=0.28,
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# 3. Leisure & Tourism Hotspots (Purple/Violet Gradient)
# ---------------------------------------------------------------------------

def create_round_trip_hotspots_chart(round_trip_df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart showing Leisure & Tourism Hotspots in Purple/Violet matching station_trip_analysis.html.
    """
    if round_trip_df.empty:
        return empty_figure("No round-trip journey data available for the selected filters.", height=CHART_HEIGHT_LEISURE)

    n_bars = len(round_trip_df)
    dynamic_height = max(CHART_HEIGHT_LEISURE, n_bars * 28 + 60)

    station_names = round_trip_df["station_name"].tolist()
    display_ticks = [_clean_short_station(name, 22) for name in station_names]

    custom_data = round_trip_df[
        ["station_name", "round_trips", "total_departures", "round_trip_pct"]
    ].values

    # Purple/Violet gradient from HTML reference
    bar_colors = [
        f"rgba(168, 85, 247, {0.45 + (i / max(1, n_bars - 1)) * 0.55:.2f})"
        for i in range(n_bars)
    ]

    hover_texts = [
        f"<b>{name}</b><br><br>"
        f"Round-Trip Ratio: <b>{pct:.1f}%</b><br>"
        f"Round Trips: <b>{r:,}</b> (out of {deps:,} total departures)<br>"
        f"<span style='color:#94A3B8;font-size:10px;'>* Trips starting and ending at this station</span>"
        for name, r, deps, pct in zip(
            station_names,
            round_trip_df["round_trips"],
            round_trip_df["total_departures"],
            round_trip_df["round_trip_pct"],
        )
    ]

    fig = go.Figure(
        go.Bar(
            x=round_trip_df["round_trip_pct"],
            y=station_names,
            orientation="h",
            marker=dict(
                color=bar_colors,
                line=dict(color="#9333ea", width=1),
            ),
            customdata=custom_data,
            text=[f"{pct:.1f}% ({r:,} loops)" for pct, r in zip(round_trip_df["round_trip_pct"], round_trip_df["round_trips"])],
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
            ticksuffix="%",
            range=[0, max(50, round_trip_df["round_trip_pct"].max() + 5)],
            showgrid=True,
            gridcolor="#f1f5f9",
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            categoryorder="array",
            categoryarray=station_names,
            tickmode="array",
            tickvals=station_names,
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
