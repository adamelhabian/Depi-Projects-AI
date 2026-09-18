"""
layout.py – Member 5 Dashboard Layout Structure
================================================
Implements the analytical hierarchy for Station & Trip Analysis:

  1. Section Header (Clear scope, Member 5 branding)
  2. Filter Panel (User Type, Region, Top N, Map Overlays, CSV Export)
  3. Station Traffic & Flow Corridor Map (Full Width)
  4. Top Stations & Top Corridors (2-Column Grid)
  5. Flow Imbalance & Leisure Hotspots (2-Column Grid)
  6. Station Profile Inspector & Smart Fleet Dispatch (2-Column Grid)
"""

from __future__ import annotations

from dash import dcc, html

from config import (
    ID_MAP,
    ID_TOP_STATIONS,
    ID_TOP_ROUTES,
    ID_FLOW_IMBALANCE,
    ID_ROUND_TRIP_CHART,
    ID_INSPECTOR_CONTAINER,
    ID_DISPATCH_CONTAINER,
    ID_SELECTED_STATION_STORE,
    CHART_HEIGHT_MAP,
    CHART_HEIGHT_BAR,
    CHART_HEIGHT_IMBALANCE,
    CHART_HEIGHT_LEISURE,
)
from components.chart_card import chart_card
from components.filter_panel import filter_panel
from components.station_inspector import render_station_inspector
from components.dispatch_panel import render_dispatch_panel


def create_layout() -> html.Div:
    """
    Construct the full Station & Trip Analysis section layout.

    Returns
    -------
    html.Div
    """
    return html.Div(
        className="m5-container",
        children=[
            # State store for clicked station across map and charts
            dcc.Store(id=ID_SELECTED_STATION_STORE, data=None),
            # ── 1. Section Header ─────────────────────────────────────────
            html.Header(
                className="mb-6",
                children=[
                    html.Div(
                        className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-200",
                        children=[
                            html.Div([
                                html.Div(
                                    className="flex items-center gap-2 mb-1",
                                    children=[
                                        html.Span("Bay Wheels System", className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200"),
                                        html.Span("SFMTA • MTC Network · Member 5", className="text-xs text-slate-400 font-medium"),
                                    ],
                                ),
                                html.H1("Station & Trip Analysis", className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight"),
                                html.P("Network traffic hubs, corridor flows, spatial rebalancing, and station deep dives.", className="text-sm sm:text-base text-slate-500 mt-1"),
                            ]),
                            html.Div(
                                className="flex items-center gap-2 text-xs font-medium",
                                children=[
                                    html.Span(
                                        [
                                            html.Span(className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse inline-block mr-1.5"),
                                            "🟢 LIVE: Supabase Cloud",
                                        ],
                                        className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 shadow-sm text-slate-700 flex items-center font-semibold",
                                    ),
                                    html.Span(
                                        "Q1-Q4 Synthesized Trip Ledger",
                                        className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 shadow-sm text-slate-500 hidden sm:inline-block",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # ── 2. Filter & Export Controls ──────────────────────────────
            filter_panel(),

            # ── 3. Station Traffic & Flow Corridor Map (Full Width) ──────
            html.Div(
                className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 sm:p-5 mb-6 relative overflow-hidden",
                children=[
                    html.Div(
                        className="flex flex-wrap items-center justify-between gap-2 mb-3",
                        children=[
                            html.Div([
                                html.H2("Station Traffic & Flow Corridor Map", className="text-lg font-bold text-slate-900"),
                                html.P(
                                    "Bubble radius represents total station trip volume; color indicates network rebalancing deficit or surplus.",
                                    className="text-xs text-slate-500",
                                ),
                            ]),
                        ],
                    ),
                    html.Div(
                        style={"position": "relative", "width": "100%", "height": f"{CHART_HEIGHT_MAP}px", "borderRadius": "10px", "overflow": "hidden", "border": "1px solid #e2e8f0"},
                        children=[
                            dcc.Graph(
                                id=ID_MAP,
                                style={"height": f"{CHART_HEIGHT_MAP}px", "width": "100%"},
                                config={
                                    "displayModeBar": "hover",
                                    "displaylogo": False,
                                    "modeBarButtonsToRemove": [
                                        "select2d",
                                        "lasso2d",
                                        "autoScale2d",
                                    ],
                                },
                            ),
                            # Slide-in Side Drawer container positioned over map
                            html.Div(
                                id=ID_INSPECTOR_CONTAINER,
                                className="station-drawer drawer-closed",
                                children=render_station_inspector(None),
                            ),
                        ],
                    ),
                ],
            ),

            # ── 4. Two-Column Analytical Charts: Volume & Corridors ──────
            html.Div(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6",
                children=[
                    chart_card(
                        graph_id=ID_TOP_STATIONS,
                        title="Top Stations by Total Traffic",
                        subtitle="Ranking stations by cumulative arrivals and departures. Percentages reflect share of active network traffic.",
                        height=CHART_HEIGHT_BAR,
                    ),
                    chart_card(
                        graph_id=ID_TOP_ROUTES,
                        title="Top Origin–Destination Corridors",
                        subtitle="Most frequently traveled station-to-station corridors across the bicycle network.",
                        height=CHART_HEIGHT_BAR,
                    ),
                ],
            ),

            # ── 5. Two-Column Analytical Charts: Imbalance & Leisure ─────
            html.Div(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6",
                children=[
                    chart_card(
                        graph_id=ID_FLOW_IMBALANCE,
                        title="Station Network Flow Imbalance",
                        subtitle="Critical stations demanding truck/van rebalancing. Identifies dock depletion vs overflow docks.",
                        height=CHART_HEIGHT_IMBALANCE,
                    ),
                    chart_card(
                        graph_id=ID_ROUND_TRIP_CHART,
                        title="Leisure & Tourism Hotspots",
                        subtitle="Stations exhibiting high percentages of loop journeys (origin = destination), signaling recreational riding.",
                        height=CHART_HEIGHT_LEISURE,
                    ),
                ],
            ),

            # ── 6. Prescriptive Fleet Dispatch & Rebalancing ────────────
            html.Div(
                className="mb-8",
                children=[
                    # Prescriptive Dispatch Rebalancing Panel
                    html.Div(
                        id=ID_DISPATCH_CONTAINER,
                        children=render_dispatch_panel([]),
                    ),
                ],
            ),
        ],
    )
