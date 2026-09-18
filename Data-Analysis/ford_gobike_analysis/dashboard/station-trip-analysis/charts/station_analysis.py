"""
charts/station_analysis.py – Popular Stations & Flow Imbalance Visualizations
=============================================================================
Plotly chart generators for:
  1. Top Stations by Total Traffic (Horizontal bar chart)
  2. Station Flow Imbalance / Inbound vs Outbound Pressure (Diverging bar chart)

Key UI & Readability Fixes:
  - Single-line labels with rank prefix ("1. ", "2. ") so labels NEVER overlap vertically.
  - Distinct unique keys prevent Plotly from merging duplicate category names.
  - Dynamic height ensures 15 and 20 bars get comfortable vertical spacing.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_BAR, CHART_HEIGHT_IMBALANCE, CHART_HEIGHT_LEISURE
from utils.theme import apply_chart_theme, empty_figure


def _clean_short_station(name: str, max_chars: int = 28) -> str:
    """Clean and abbreviate station names for single-line display."""
    s = str(name).strip()
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
# 1. Top Stations by Total Traffic
# ---------------------------------------------------------------------------

def create_top_stations_chart(top_stations: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart showing Top N stations ranked by total traffic.

    Parameters
    ----------
    top_stations : pd.DataFrame
        Output of compute_top_stations(); sorted ascending by total_traffic.

    Returns
    -------
    go.Figure
    """
    if top_stations.empty:
        return empty_figure("No station data available for the selected filters.", height=CHART_HEIGHT_BAR)

    n_bars = len(top_stations)

    # Dynamic height: gives each bar at least 26px of vertical breathing room
    dynamic_height = max(CHART_HEIGHT_BAR, n_bars * 26 + 80)

    station_names = top_stations["station_name"].tolist()

    # Generate single-line labels with rank prefix (1 = highest traffic at top)
    display_ticks = [
        f"{n_bars - i}. {_clean_short_station(name, 28)}"
        for i, name in enumerate(station_names)
    ]

    custom_data = top_stations[
        ["station_name", "departures", "arrivals", "net_flow"]
    ].values

    fig = go.Figure(
        go.Bar(
            x=top_stations["total_traffic"],
            y=station_names,  # Unique station key
            orientation="h",
            marker=dict(
                color=top_stations["total_traffic"],
                colorscale=[
                    [0.0, "#A3E635"],
                    [1.0, "#059669"],
                ],
                showscale=False,
                line=dict(width=0),
            ),
            customdata=custom_data,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br><br>"
                "Total Traffic: <b>%{x:,}</b><br>"
                "Departures: <b>%{customdata[1]:,}</b><br>"
                "Arrivals: <b>%{customdata[2]:,}</b><br>"
                "Net Flow: <b>%{customdata[3]:+,}</b>"
                "<extra></extra>"
            ),
            text=top_stations["total_traffic"].apply(lambda v: f"{v:,}"),
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
            title="Total Trips (Departures + Arrivals)",
            tickformat=",",
            showgrid=True,
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            categoryorder="array",
            categoryarray=station_names,
            tickmode="array",
            tickvals=station_names,
            ticktext=display_ticks,
            tickfont=dict(color=COLORS["text_secondary"], size=11),
        ),
        bargap=0.25,
    )

    return fig


# ---------------------------------------------------------------------------
# 2. Station Flow Imbalance (Inbound vs Outbound Pressure)
# ---------------------------------------------------------------------------

def create_flow_imbalance_chart(flow_imbalance: pd.DataFrame) -> go.Figure:
    """
    Diverging horizontal bar chart displaying network flow imbalance.

    Parameters
    ----------
    flow_imbalance : pd.DataFrame
        Output of compute_flow_imbalance(); sorted by net_flow ascending.

    Returns
    -------
    go.Figure
    """
    if flow_imbalance.empty:
        return empty_figure("No flow imbalance data available for the selected filters.", height=CHART_HEIGHT_IMBALANCE)

    n_bars = len(flow_imbalance)
    dynamic_height = max(CHART_HEIGHT_IMBALANCE, n_bars * 26 + 90)

    station_names = flow_imbalance["station_name"].tolist()
    display_ticks = [_clean_short_station(name, 32) for name in station_names]

    bar_colors = [
        COLORS["danger"] if val < 0 else COLORS["success"]
        for val in flow_imbalance["net_flow"]
    ]

    custom_data = flow_imbalance[
        ["station_name", "departures", "arrivals", "imbalance_type"]
    ].values

    fig = go.Figure(
        go.Bar(
            x=flow_imbalance["net_flow"],
            y=station_names,
            orientation="h",
            marker=dict(
                color=bar_colors,
                opacity=0.88,
                line=dict(width=0),
            ),
            customdata=custom_data,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br><br>"
                "Flow Category: <b>%{customdata[3]}</b><br>"
                "Net Flow: <b>%{x:+,}</b><br>"
                "Departures: <b>%{customdata[1]:,}</b><br>"
                "Arrivals: <b>%{customdata[2]:,}</b>"
                "<extra></extra>"
            ),
            text=flow_imbalance["net_flow"].apply(lambda v: f"{v:+,}"),
            textposition="auto",
            textfont=dict(color=COLORS["text_primary"], size=10),
        )
    )

    # Vertical zero baseline
    fig.add_vline(
        x=0,
        line_width=2,
        line_color="#CBD5E1",
        line_dash="dash",
    )

    fig = apply_chart_theme(
        fig,
        height=dynamic_height,
        margin=dict(l=10, r=40, t=40, b=36),
    )

    fig.update_layout(
        xaxis=dict(
            title="← Outbound Pressure (Deficit)   |   Inbound Pressure (Surplus) →",
            tickformat=",",
            showgrid=True,
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
            tickfont=dict(color=COLORS["text_secondary"], size=11),
        ),
        bargap=0.28,
                annotations=[
            dict(
                x=0.0,
                y=1.07,
                xref="paper",
                yref="paper",
                text="← Deficit (Outbound)",
                showarrow=False,
                font=dict(size=11, color=COLORS["danger"], weight="bold"),
                xanchor="left",
            ),
            dict(
                x=1.0,
                y=1.07,
                xref="paper",
                yref="paper",
                text="Surplus (Inbound) →",
                showarrow=False,
                font=dict(size=11, color=COLORS["accent_dim"], weight="bold"),
                xanchor="right",
            ),
        ],
    )

    return fig


# ---------------------------------------------------------------------------
# 3. Leisure & Tourism Hotspots (Round-Trip Journeys)
# ---------------------------------------------------------------------------

def create_round_trip_hotspots_chart(round_trip_df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart showing Leisure & Tourism Hotspots (Round-Trip Journeys).

    Parameters
    ----------
    round_trip_df : pd.DataFrame
        Output of compute_round_trip_hotspots(); sorted by round_trips ascending.

    Returns
    -------
    go.Figure
    """
    if round_trip_df.empty:
        return empty_figure("No round-trip journey data available for the selected filters.", height=CHART_HEIGHT_LEISURE)

    n_bars = len(round_trip_df)
    dynamic_height = max(CHART_HEIGHT_LEISURE, n_bars * 26 + 80)

    station_names = round_trip_df["station_name"].tolist()
    display_ticks = [
        f"{n_bars - i}. {_clean_short_station(name, 28)}"
        for i, name in enumerate(station_names)
    ]

    custom_data = round_trip_df[
        ["station_name", "round_trips", "total_departures", "round_trip_pct"]
    ].values

    fig = go.Figure(
        go.Bar(
            x=round_trip_df["round_trips"],
            y=station_names,
            orientation="h",
            marker=dict(
                color=round_trip_df["round_trip_pct"],
                colorscale=[
                    [0.0, "#A3E635"],
                    [1.0, "#0D9488"],
                ],
                showscale=False,
                line=dict(width=0),
            ),
            customdata=custom_data,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br><br>"
                "Round Trips: <b>%{x:,}</b><br>"
                "Total Departures: <b>%{customdata[2]:,}</b><br>"
                "Round-Trip Ratio: <b>%{customdata[3]:.1f}%</b>"
                "<extra></extra>"
            ),
            text=[
                f"{r:,} ({pct:.1f}%)"
                for r, pct in zip(round_trip_df["round_trips"], round_trip_df["round_trip_pct"])
            ],
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
            title="Round Trips (Start == End Station)",
            tickformat=",",
            showgrid=True,
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            categoryorder="array",
            categoryarray=station_names,
            tickmode="array",
            tickvals=station_names,
            ticktext=display_ticks,
            tickfont=dict(color=COLORS["text_secondary"], size=11),
        ),
        bargap=0.25,
    )

    return fig
