"""
pages/station_page.py – Modernized Station & Network Flow Analysis View
========================================================================
Enterprise station network diagnostics:
  1. Controls Bar: Top-N slider (5-30), Corridor toggle (OD flow lines)
  2. Map & Station Profile Drawer (interactive Scattermap + slide-in detail panel)
  3. 4 Full-Name Horizontal Bar Charts:
     - Top Busiest Stations
     - Top Deficit Stations (Orange)
     - Top Surplus Stations (Blue)
     - Top Round-Trip Loop Stations (Purple)
  4. Smart Fleet Rebalancing Dispatch Grid with CSV Export
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd

from config import (
    ID_STATION_TOPN_SLIDER,
    ID_STATION_CORRIDOR_TOGGLE,
    ID_STATION_MAP,
    ID_STATION_DRAWER,
    ID_STATION_DRAWER_CONTENT,
    ID_STATION_DRAWER_CLOSE,
    ID_STATION_CHART_BUSIEST,
    ID_STATION_CHART_DEFICIT,
    ID_STATION_CHART_SURPLUS,
    ID_STATION_CHART_LOOPS,
    ID_STATION_REBALANCING_CONTAINER,
    ID_STATION_REBALANCING_DOWNLOAD_BTN,
    ID_STATION_REBALANCING_DOWNLOAD,
)
from components.chart_card import render_chart_card
from utils.theme import apply_chart_theme, COLORS
from data_loader import load_station_analytics_data


def build_station_map_figure(
    stations_df: pd.DataFrame,
    corridors: List[Dict[str, Any]],
    show_corridors: bool = True,
) -> go.Figure:
    """Builds the primary interactive Mapbox network map with backward/forward compatibility."""
    fig = go.Figure()

    if stations_df.empty:
        return fig

    # Compatibility between Plotly 7+ (Scattermap) and Plotly 5/6 (Scattermapbox)
    ScatterMapCls = getattr(go, "Scattermap", getattr(go, "Scattermapbox", None))
    is_new_map = hasattr(go, "Scattermap")

    # 1. Optional Transit Corridor Lines
    if show_corridors and corridors:
        for c in corridors[:20]:
            fig.add_trace(
                ScatterMapCls(
                    lat=[c["from_lat"], c["to_lat"]],
                    lon=[c["from_lng"], c["to_lng"]],
                    mode="lines",
                    line=dict(width=max(1.5, min(4.5, c["trips"] / 250)), color="rgba(99, 102, 241, 0.45)"),
                    hoverinfo="text",
                    text=f"Transit Corridor: {c['from_name']} -> {c['to_name']} ({c['trips']:,} trips)",
                    showlegend=False,
                )
            )

    # 2. Station Markers (sized by total volume, colored by net flow)
    max_flow = stations_df["total_flow"].max() or 1
    sizes = [max(8, min(24, int((f / max_flow) * 22) + 7)) for f in stations_df["total_flow"]]

    customdata = list(
        zip(
            stations_df["name"],
            stations_df["region"],
            stations_df["total_flow"],
            stations_df["net_flow"],
            stations_df["capacity"],
            stations_df["loop_ratio"],
        )
    )

    # Diverging color scale: Orange (Deficit) -> Slate (Balanced) -> Blue (Surplus)
    fig.add_trace(
        ScatterMapCls(
            lat=stations_df["lat"],
            lon=stations_df["lng"],
            mode="markers",
            marker=dict(
                size=sizes,
                color=stations_df["net_flow"],
                colorscale=[
                    [0.0, COLORS["deficit"]],
                    [0.45, "#FDA4AF"],
                    [0.5, COLORS["balanced"]],
                    [0.55, "#93C5FD"],
                    [1.0, COLORS["surplus"]],
                ],
                cmin=-1200,
                cmax=1200,
                colorbar=dict(
                    title=dict(text="Net Flow (Arr - Dep)", font=dict(size=10, family="Inter")),
                    thickness=12,
                    len=0.7,
                    x=0.98,
                    y=0.5,
                    tickfont=dict(size=9, family="Inter"),
                ),
                opacity=0.9,
            ),
            text=stations_df["name"],
            customdata=customdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Region: %{customdata[1]}<br>"
                "Total Trips: <b>%{customdata[2]:,}</b><br>"
                "Net Flow: <b>%{customdata[3]:+d}</b><br>"
                "Estimated Docks: <b>%{customdata[4]}</b> docks<br>"
                "<span style='color:#38BDF8;'>Click station to open profile drawer</span>"
                "<extra></extra>"
            ),
            name="Stations",
            showlegend=False,
        )
    )

    map_cfg = dict(
        style="carto-positron",
        center=dict(lat=37.7780, lon=-122.3500),
        zoom=10.2,
    )

    layout_kwargs = {"map": map_cfg} if is_new_map else {"mapbox": map_cfg}

    fig.update_layout(
        **layout_kwargs,
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor=COLORS["tooltip_bg"],
            font=dict(family="Inter", size=12, color="#FFFFFF"),
        ),
    )

    return fig


def build_busiest_stations_figure(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Top N Busiest Stations by total trip turnover."""
    top_df = df.nlargest(top_n, "total_flow").sort_values("total_flow", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=top_df["total_flow"],
            y=top_df["name"],
            orientation="h",
            marker=dict(color=COLORS["subscriber"], line=dict(color="rgba(0,0,0,0.08)", width=1)),
            text=[f"{v:,}" for v in top_df["total_flow"]],
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Total Rides: %{x:,}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Total Trips (Arrivals + Departures)"),
        margin=dict(l=220, r=20, t=15, b=30),
    )
    return apply_chart_theme(fig, height=280)


def build_deficit_stations_figure(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Top N Deficit Stations (departures exceed arrivals, need inbound bikes)."""
    top_df = df[df["net_flow"] < 0].nsmallest(top_n, "net_flow").sort_values("net_flow", ascending=False)
    fig = go.Figure(
        go.Bar(
            x=top_df["net_flow"],
            y=top_df["name"],
            orientation="h",
            marker=dict(color=COLORS["deficit"], line=dict(color="rgba(0,0,0,0.08)", width=1)),
            text=[f"{v:+d}" for v in top_df["net_flow"]],
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Net Deficit: %{x:+d} bikes<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Net Deficit (Dock Depletion)"),
        margin=dict(l=220, r=20, t=15, b=30),
    )
    return apply_chart_theme(fig, height=280)


def build_surplus_stations_figure(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Top N Surplus Stations (arrivals exceed departures, need outbound clearance)."""
    top_df = df[df["net_flow"] > 0].nlargest(top_n, "net_flow").sort_values("net_flow", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=top_df["net_flow"],
            y=top_df["name"],
            orientation="h",
            marker=dict(color=COLORS["surplus"], line=dict(color="rgba(0,0,0,0.08)", width=1)),
            text=[f"{v:+d}" for v in top_df["net_flow"]],
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Net Surplus: %{x:+d} bikes<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Net Surplus (Dock Overflow)"),
        margin=dict(l=220, r=20, t=15, b=30),
    )
    return apply_chart_theme(fig, height=280)


def build_loops_stations_figure(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Top N Round-Trip Loop Stations (High tourist/recreation ratio)."""
    top_df = df[df["total_flow"] > 200].nlargest(top_n, "loop_ratio").sort_values("loop_ratio", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=top_df["loop_ratio"] * 100,
            y=top_df["name"],
            orientation="h",
            marker=dict(color=COLORS["customer"], line=dict(color="rgba(0,0,0,0.08)", width=1)),
            text=[f"{v*100:.1f}%" for v in top_df["loop_ratio"]],
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Loop Return Rate: %{x:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Loop Ratio (% Trips Returning to Same Station)"),
        margin=dict(l=220, r=20, t=15, b=30),
    )
    return apply_chart_theme(fig, height=280)


def render_station_drawer(station_info: Optional[Dict[str, Any]] = None) -> html.Div:
    """Renders the slide-in Station Profile Drawer content."""
    if not station_info:
        return html.Div(
            className="p-6 text-center text-slate-400 flex flex-col items-center justify-center h-full",
            children=[
                html.Div(
                    className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-3",
                    children=[html.I(className="fas fa-crosshairs text-lg")],
                ),
                html.H4("No Station Selected", className="text-sm font-bold text-slate-700 mb-1"),
                html.P(
                    "Click any marker on the map to inspect dock capacity, arrival/departure bias, and corridor flow.",
                    className="text-xs text-slate-500 max-w-[220px] leading-relaxed",
                ),
            ],
        )

    name = station_info.get("name", "Unknown Station")
    region = station_info.get("region", "San Francisco")
    total_trips = station_info.get("total_flow", 0)
    net_flow = station_info.get("net_flow", 0)
    capacity = station_info.get("capacity", 25)
    loop_ratio = station_info.get("loop_ratio", 0.04)

    is_deficit = net_flow < 0
    bias_color = "bg-orange-50 text-orange-700 border-orange-200" if is_deficit else "bg-blue-50 text-blue-700 border-blue-200"
    bias_label = f"Deficit: {net_flow:+d} bikes" if is_deficit else f"Surplus: {net_flow:+d} bikes"
    action_rec = (
        "Inbound Rebalancing Priority: Dispatch 12-18 bikes prior to morning rush (07:00 AM)"
        if is_deficit
        else "Outbound Clearance Priority: Sweep 10-15 bikes by 09:30 AM to prevent dock lockout"
    )

    return html.Div(
        className="p-5 flex flex-col justify-between h-full space-y-4",
        children=[
            # Header
            html.Div(
                children=[
                    html.Div(
                        className="flex items-center justify-between mb-2",
                        children=[
                            html.Span(region, className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600"),
                            html.Span(bias_label, className=f"text-[10px] font-bold px-2 py-0.5 rounded-full border {bias_color}"),
                        ],
                    ),
                    html.H3(name, className="text-base font-bold text-slate-900 leading-tight"),
                ],
            ),

            # Core Metrics
            html.Div(
                className="grid grid-cols-2 gap-2 bg-slate-50 rounded-xl p-3 border border-slate-100",
                children=[
                    html.Div([html.Div("Total Trips", className="text-[10px] text-slate-400 uppercase font-semibold"), html.Div(f"{total_trips:,}", className="text-sm font-bold text-slate-800 font-mono")]),
                    html.Div([html.Div("Dock Capacity", className="text-[10px] text-slate-400 uppercase font-semibold"), html.Div(f"{capacity} docks", className="text-sm font-bold text-slate-800 font-mono")]),
                    html.Div([html.Div("Net Imbalance", className="text-[10px] text-slate-400 uppercase font-semibold"), html.Div(f"{net_flow:+d}", className="text-sm font-bold text-slate-800 font-mono")]),
                    html.Div([html.Div("Loop Trip Rate", className="text-[10px] text-slate-400 uppercase font-semibold"), html.Div(f"{loop_ratio*100:.1f}%", className="text-sm font-bold text-slate-800 font-mono")]),
                ],
            ),

            # Recommended Action
            html.Div(
                className=f"p-3 rounded-xl border text-xs leading-relaxed {bias_color}",
                children=[
                    html.Div("⚡ Operational Dispatch Directive:", className="font-bold text-[11px] mb-1"),
                    html.P(action_rec, className="text-[11px]"),
                ],
            ),
        ],
    )


def render_station_page() -> html.Div:
    """
    Renders the modern Station & Network Flow dashboard page.
    """
    data = load_station_analytics_data()
    stns_df = data.get("stations_df", pd.DataFrame())
    corridors = data.get("corridors", [])
    rebalancing = data.get("rebalancing", [])

    map_fig = build_station_map_figure(stns_df, corridors, show_corridors=True)
    busiest_fig = build_busiest_stations_figure(stns_df, top_n=10)
    deficit_fig = build_deficit_stations_figure(stns_df, top_n=10)
    surplus_fig = build_surplus_stations_figure(stns_df, top_n=10)
    loops_fig = build_loops_stations_figure(stns_df, top_n=10)

    # Rebalancing Cards
    rebal_card_items = []
    for item in rebalancing[:6]:
        card = html.Div(
            className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow",
            children=[
                # Top: Rank + Region + Priority Badge
                html.Div(
                    className="flex items-center justify-between mb-2.5",
                    children=[
                        html.Div(
                            className="flex items-center gap-2",
                            children=[
                                html.Span(f"#{item['rank']}", className="text-xs font-bold text-slate-400 font-mono"),
                                html.Span(item["region"], className="text-[10px] uppercase font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full"),
                            ],
                        ),
                        html.Span(
                            item["priority"],
                            className=f"text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full border {item['badge_style']}",
                        ),
                    ],
                ),

                # Flow Row: Surplus -> Deficit
                html.Div(
                    className="my-2 space-y-1.5",
                    children=[
                        html.Div(
                            className="flex items-center gap-2 text-xs",
                            children=[
                                html.Span("SURPLUS", className="text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 shrink-0"),
                                html.Span(item["surplus_station"], className="font-semibold text-slate-800 truncate text-[11px]"),
                            ],
                        ),
                        html.Div(
                            className="flex items-center justify-center text-slate-400 text-xs py-0.5",
                            children=[html.I(className="fas fa-arrow-down text-slate-400")],
                        ),
                        html.Div(
                            className="flex items-center gap-2 text-xs",
                            children=[
                                html.Span("DEFICIT", className="text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-orange-100 text-orange-700 shrink-0"),
                                html.Span(item["deficit_station"], className="font-semibold text-slate-800 truncate text-[11px]"),
                            ],
                        ),
                    ],
                ),

                # Metrics Footer
                html.Div(
                    className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs",
                    children=[
                        html.Div(
                            [
                                html.Span("Distance: ", className="text-slate-400 text-[11px]"),
                                html.Span(f"{item['distance_km']} km", className="font-bold text-slate-700 font-mono text-[11px]"),
                            ]
                        ),
                        html.Div(
                            [
                                html.Span("Transfer: ", className="text-slate-400 text-[11px]"),
                                html.Span(f"~{item['transfer_bikes']} bikes", className="font-extrabold text-blue-600 font-mono text-[11px]"),
                            ]
                        ),
                    ],
                ),
            ],
        )
        rebal_card_items.append(card)

    return html.Div(
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6",
        children=[
            # Hidden download component for CSV export
            dcc.Download(id=ID_STATION_REBALANCING_DOWNLOAD),

            # Page Header & Controls Bar
            html.Div(
                className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4",
                children=[
                    html.Div(
                        children=[
                            html.H2("Station & Network Flow Analysis", className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight"),
                            html.P("Geospatial demand heat, OD transit corridors, dock saturation imbalances, and dispatch planning", className="text-xs text-slate-500 mt-0.5"),
                        ],
                    ),

                    # Interactive Controls
                    html.Div(
                        className="flex flex-wrap items-center gap-5",
                        children=[
                            # Top-N Slider
                            html.Div(
                                className="flex items-center gap-2",
                                children=[
                                    html.Span("Top Stations:", className="text-xs font-semibold text-slate-600"),
                                    html.Div(
                                        className="w-28",
                                        children=[
                                            dcc.Slider(
                                                id=ID_STATION_TOPN_SLIDER,
                                                min=5,
                                                max=30,
                                                step=5,
                                                value=10,
                                                marks={5: "5", 10: "10", 20: "20", 30: "30"},
                                            ),
                                        ],
                                    ),
                                ],
                            ),

                            # Corridor Toggle
                            html.Div(
                                className="flex items-center gap-2",
                                children=[
                                    dcc.Checklist(
                                        id=ID_STATION_CORRIDOR_TOGGLE,
                                        options=[{"label": " Transit Corridors", "value": "SHOW"}],
                                        value=["SHOW"],
                                        className="text-xs font-semibold text-slate-700 select-none",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # Top Section: Main Geospatial Map + Slide-in Station Profile Drawer
            html.Div(
                className="grid grid-cols-1 lg:grid-cols-4 gap-6",
                children=[
                    # Map Visualizer (3 columns)
                    html.Div(
                        className="lg:col-span-3 bg-white rounded-xl border border-slate-200/80 overflow-hidden shadow-sm flex flex-col",
                        children=[
                            html.Div(
                                className="px-5 py-3 border-b border-slate-100 flex items-center justify-between bg-slate-50/50",
                                children=[
                                    html.Div(
                                        className="flex items-center gap-2",
                                        children=[
                                            html.I(className="fas fa-map-marked-alt text-teal-600 text-sm"),
                                            html.H3("Bay Area Docking Network Map", className="text-sm font-semibold text-slate-800"),
                                        ],
                                    ),
                                    html.Span("Click any station marker for profile drawer", className="text-[11px] text-slate-400 hidden sm:inline"),
                                ],
                            ),
                            dcc.Graph(
                                id=ID_STATION_MAP,
                                figure=map_fig,
                                config={"displayModeBar": True, "scrollZoom": True},
                                style={"height": "480px", "width": "100%"},
                            ),
                        ],
                    ),

                    # Station Profile Drawer (1 column)
                    html.Div(
                        id=ID_STATION_DRAWER,
                        className="lg:col-span-1 bg-white rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between min-h-[480px]",
                        children=[
                            html.Div(
                                id=ID_STATION_DRAWER_CONTENT,
                                className="h-full",
                                children=render_station_drawer(None),
                            ),
                        ],
                    ),
                ],
            ),

            # Middle Section: 4 Horizontal Bar Charts (Grid 2x2)
            html.Div(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6",
                children=[
                    # 1. Top Busiest Stations
                    render_chart_card(
                        title="Top Busiest Stations",
                        graph_id=ID_STATION_CHART_BUSIEST,
                        figure=busiest_fig,
                        subtitle="Ranked by total turnover volume (Departures + Arrivals)",
                        tooltip="Shows the highest traffic hubs across the entire Bay Area network",
                        height=280,
                    ),

                    # 2. Top Deficit Stations
                    render_chart_card(
                        title="Top Deficit Stations (Needs Replenishment)",
                        graph_id=ID_STATION_CHART_DEFICIT,
                        figure=deficit_fig,
                        subtitle="Departures drastically exceed arrivals — docks risk depletion",
                        tooltip="Stations where outbound trips exceed inbound arrivals, requiring morning bike injection",
                        height=280,
                    ),

                    # 3. Top Surplus Stations
                    render_chart_card(
                        title="Top Surplus Stations (Needs Clearance)",
                        graph_id=ID_STATION_CHART_SURPLUS,
                        figure=surplus_fig,
                        subtitle="Arrivals drastically exceed departures — docks risk saturation",
                        tooltip="Stations where inbound commuter arrivals accumulate, locking out returning riders",
                        height=280,
                    ),

                    # 4. Top Round-Trip Loop Stations
                    render_chart_card(
                        title="Top Round-Trip Loop Stations",
                        graph_id=ID_STATION_CHART_LOOPS,
                        figure=loops_fig,
                        subtitle="Percentage of trips starting and ending at the exact same hub",
                        tooltip="Identifies waterfront and scenic recreational hubs with high non-commuter loop journeys",
                        height=280,
                    ),
                ],
            ),

            # Bottom Section: Smart Fleet Rebalancing Dispatch Grid
            html.Div(
                className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-4",
                children=[
                    # Rebalancing Header & CSV Export Button
                    html.Div(
                        className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100",
                        children=[
                            html.Div(
                                children=[
                                    html.Div(
                                        className="flex items-center gap-2",
                                        children=[
                                            html.I(className="fas fa-truck text-blue-600 text-sm"),
                                            html.H3("Smart Fleet Rebalancing Dispatch Grid", className="text-base font-bold text-slate-800"),
                                        ],
                                    ),
                                    html.P(
                                        "Algorithmic pairing between dock-overflow surplus hubs and depleted deficit stations",
                                        className="text-xs text-slate-500 mt-0.5",
                                    ),
                                ],
                            ),

                            # Export CSV Button
                            html.Button(
                                [
                                    html.I(className="fas fa-download mr-1.5 text-xs"),
                                    "Export Rebalancing Plan (CSV)",
                                ],
                                id=ID_STATION_REBALANCING_DOWNLOAD_BTN,
                                n_clicks=0,
                                className="inline-flex items-center text-xs font-semibold px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white transition-colors shadow-xs self-start sm:self-auto",
                            ),
                        ],
                    ),

                    # Rebalancing Cards Grid
                    html.Div(
                        id=ID_STATION_REBALANCING_CONTAINER,
                        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
                        children=rebal_card_items,
                    ),
                ],
            ),
        ],
    )
