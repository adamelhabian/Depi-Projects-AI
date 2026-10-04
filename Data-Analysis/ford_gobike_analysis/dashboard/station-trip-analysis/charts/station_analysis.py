"""
charts/station_analysis.py – Popular Stations & Flow Imbalance Visualizations
=============================================================================
Plotly chart generators styled with Chart.js-like Tailwind aesthetic matching station_trip_analysis.html:
  1. Top Stations by Total Traffic (strictly sorted Rank 1 to Rank N, emerald gradient)
  2. Station Flow Imbalance (strictly sorted highest surplus to largest deficit, zero baseline)
  3. Leisure & Tourism Hotspots (strictly sorted by round-trip %, purple/violet gradient)
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_BAR, CHART_HEIGHT_IMBALANCE, CHART_HEIGHT_LEISURE
from utils.theme import (
    apply_chart_theme,
    empty_figure,
    COLOR_DEFICIT,
    COLOR_DEFICIT_BORDER,
    COLOR_SURPLUS,
    COLOR_SURPLUS_BORDER,
)


def _clean_short_station(name: str) -> str:
    """Clean and abbreviate station prefixes without truncation or ellipses."""
    s = str(name).strip()
    s = (
        s.replace("San Francisco ", "SF ")
        .replace("Station", "Stn")
        .replace("BART Station", "BART")
        .replace("BART ", "")
        .replace("Caltrain Station", "Caltrain")
    )
    if "(" in s and ")" in s:
        main_part = s.split("(")[0].strip()
        paren = s.split("(")[1].split(")")[0].strip()
        paren = paren.replace("Market St at ", "").replace("St at ", "/")
        s = f"{main_part} ({paren})"
    return s


# ---------------------------------------------------------------------------
# 1. Top Stations by Total Traffic (Emerald Rank-Opacity Gradient)
# ---------------------------------------------------------------------------

def create_top_stations_chart(
    top_stations: pd.DataFrame,
    total_network_traffic: int = 0,
) -> go.Figure:
    """
    Horizontal bar chart strictly ordered from Rank 1 (top) down to Rank N (bottom).
    """
    if top_stations.empty:
        return empty_figure("No station data available for the selected filters.", height=CHART_HEIGHT_BAR)

    n_bars = len(top_stations)
    # Dynamic height gives each bar ~28px of height so Top 20 never overlaps
    dynamic_height = max(340, n_bars * 28 + 60)

    station_names = top_stations["station_name"].tolist()

    display_ticks = [
        _clean_short_station(name)
        for name in station_names
    ]

    # Rank-opacity emerald gradient: top bar (Rank 1) is 1.0, descending to 0.45
    bar_colors = [
        f"rgba(16, 185, 129, {1.0 - (i / max(1, n_bars - 1)) * 0.55:.2f})"
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
        margin=dict(l=180, r=30, t=10, b=30),
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
            categoryarray=station_names,
            tickmode="array",
            tickvals=station_names,
            ticktext=display_ticks,
            tickfont=dict(color="#334155", size=11, family="Inter"),
            autorange="reversed",  # Rank 1 at top, Rank N at bottom
        ),
        bargap=0.22,
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# 2. Station Flow Imbalance (Strictly Ordered: Surplus to Deficit)
# ---------------------------------------------------------------------------

def create_flow_imbalance_chart(flow_imbalance: pd.DataFrame) -> go.Figure:
    """
    Diverging horizontal bar chart ordered strictly from highest surplus down to largest deficit.
    Surplus = Blue #3B82F6 (bike clearance needed)
    Deficit = Orange #F97316 (bike re-stocking needed)
    """
    if flow_imbalance.empty:
        return empty_figure("No flow imbalance data available for the selected filters.", height=CHART_HEIGHT_IMBALANCE)

    n_bars = len(flow_imbalance)
    dynamic_height = max(340, n_bars * 28 + 60)

    station_names = flow_imbalance["station_name"].tolist()
    display_ticks = [_clean_short_station(name) for name in station_names]

    bar_colors = [
        COLOR_SURPLUS if val >= 0 else COLOR_DEFICIT
        for val in flow_imbalance["net_flow"]
    ]
    border_colors = [
        COLOR_SURPLUS_BORDER if val >= 0 else COLOR_DEFICIT_BORDER
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
        margin=dict(l=180, r=30, t=10, b=30),
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
            automargin=True,
            categoryorder="array",
            categoryarray=station_names,
            tickmode="array",
            tickvals=station_names,
            ticktext=display_ticks,
            tickfont=dict(color="#334155", size=11, family="Inter"),
            autorange="reversed",  # Surplus at top, Deficit at bottom
        ),
        bargap=0.22,
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# 3. Leisure & Tourism Hotspots (Strictly Ordered by Round-Trip %)
# ---------------------------------------------------------------------------

def create_round_trip_hotspots_chart(round_trip_df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart strictly sorted by round-trip ratio from highest (top) to lowest.
    """
    if round_trip_df.empty:
        return empty_figure("No round-trip journey data available for the selected filters.", height=CHART_HEIGHT_LEISURE)

    n_bars = len(round_trip_df)
    dynamic_height = max(340, n_bars * 28 + 60)

    station_names = round_trip_df["station_name"].tolist()
    display_ticks = [_clean_short_station(name) for name in station_names]

    custom_data = round_trip_df[
        ["station_name", "round_trips", "total_departures", "round_trip_pct"]
    ].values

    # Purple/Violet gradient from 1.0 (top) down to 0.45
    bar_colors = [
        f"rgba(168, 85, 247, {1.0 - (i / max(1, n_bars - 1)) * 0.55:.2f})"
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

    # Modern Lollipop Chart (Stem + Glowing Circle Node) for high-end visual variety
    fig = go.Figure()

    # 1. Horizontal stems (bars with slim width)
    fig.add_trace(
        go.Bar(
            x=round_trip_df["round_trip_pct"],
            y=station_names,
            orientation="h",
            width=0.15,
            marker=dict(
                color="rgba(168, 85, 247, 0.4)",
                line=dict(width=0),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # 2. Glowing circular lollipop markers at the tip
    fig.add_trace(
        go.Scatter(
            x=round_trip_df["round_trip_pct"],
            y=station_names,
            mode="markers+text",
            marker=dict(
                size=18,
                color="#A855F7",
                line=dict(color="#FFFFFF", width=2),
                symbol="circle",
            ),
            customdata=custom_data,
            text=[f"  {pct:.1f}% ({r:,} loops)" for pct, r in zip(round_trip_df["round_trip_pct"], round_trip_df["round_trips"])],
            textposition="middle right",
            textfont=dict(color="#0F172A", size=10.5, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
            showlegend=False,
        )
    )

    fig = apply_chart_theme(
        fig,
        height=dynamic_height,
        margin=dict(l=180, r=40, t=10, b=30),
    )

    fig.update_layout(
        xaxis=dict(
            title="",
            ticksuffix="%",
            range=[0, max(35, round_trip_df["round_trip_pct"].max() + 12)],
            showgrid=True,
            gridcolor="#f1f5f9",
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            automargin=True,
            categoryorder="array",
            categoryarray=station_names,
            tickmode="array",
            tickvals=station_names,
            ticktext=display_ticks,
            tickfont=dict(color="#334155", size=11, family="Inter"),
            autorange="reversed",
        ),
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig
