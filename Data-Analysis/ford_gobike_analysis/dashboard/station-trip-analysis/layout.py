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
            html.Div(
                className="section-header",
                children=[
                    html.H2("Station & Trip Analysis", className="section-title"),
                    html.P(
                        "Youssef Mohamed Member 5 · Network traffic hubs, corridor flows, spatial rebalancing, and station deep dives.",
                        className="section-subtitle",
                    ),
                ],
            ),

            # ── 2. Filter & Export Controls ──────────────────────────────
            filter_panel(),

            # ── 3. Station Traffic & Flow Corridor Map (Full Width) ──────
            html.Div(
                className="grid-full",
                children=[
                    chart_card(
                        graph_id=ID_MAP,
                        title="Station Traffic & Flow Corridor Map",
                        subtitle="Marker size indicates total traffic; color indicates net flow (inbound vs outbound pressure). Purple lines connect top origin–destination transit corridors.",
                        height=CHART_HEIGHT_MAP,
                    ),
                ],
            ),

            # ── 4. Two-Column Analytical Charts: Volume & Corridors ──────
            html.Div(
                className="grid-two-col",
                children=[
                    chart_card(
                        graph_id=ID_TOP_STATIONS,
                        title="Top Stations by Total Traffic",
                        subtitle="Stations with the highest combined departure and arrival volume across the network.",
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
                className="grid-two-col",
                children=[
                    chart_card(
                        graph_id=ID_FLOW_IMBALANCE,
                        title="Station Network Flow Imbalance",
                        subtitle="Outbound pressure (net deficit) vs Inbound pressure (net surplus).",
                        height=CHART_HEIGHT_IMBALANCE,
                    ),
                    chart_card(
                        graph_id=ID_ROUND_TRIP_CHART,
                        title="Leisure & Tourism Hotspots",
                        subtitle="Stations with high round-trip ratios (start == end), characteristic of recreational and tourist riding.",
                        height=CHART_HEIGHT_LEISURE,
                    ),
                ],
            ),

            # ── 6. Interactive Inspector & Prescriptive Dispatch ────────
            html.Div(
                className="grid-two-col",
                children=[
                    # Station Profile Inspector (Populated via clickData)
                    html.Div(
                        id=ID_INSPECTOR_CONTAINER,
                        children=render_station_inspector(None),
                    ),

                    # Prescriptive Dispatch Rebalancing Panel
                    html.Div(
                        id=ID_DISPATCH_CONTAINER,
                        children=render_dispatch_panel([]),
                    ),
                ],
            ),
        ],
    )
