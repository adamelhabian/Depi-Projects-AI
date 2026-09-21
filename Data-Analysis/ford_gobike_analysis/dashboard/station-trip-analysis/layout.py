"""
layout.py – Section Layout for Member 5: Station & Trip Analysis
================================================================
Tailwind CSS-driven layout perfectly matching station_trip_analysis.html and reference UI:
  1. Top Controls Bar: Top-N Rankings slider (5-30) + Corridor vectors toggle + Fit Entire Bay Area + Export CSV.
  2. Interactive Geospatial Map (500px) with Floating Map Legend & Slide-in Station Profile Drawer.
  3. Top Stations by Total Traffic & Top Origin–Destination Corridors (side-by-side).
  4. Station Network Flow Imbalance & Leisure & Tourism Hotspots (side-by-side).
  5. Prescriptive Fleet Dispatch & Rebalancing Panel.
  6. Zero duplicate headers or redundant filter dropdowns (driven by sticky Global Filter Bar).
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
    ID_USER_FILTER,
    ID_REGION_FILTER,
    ID_TOP_N_SLIDER,
    ID_MAP_FLOW_LINES_TOGGLE,
    ID_DOWNLOAD_BTN,
    ID_DOWNLOAD_DATA,
    DEFAULT_TOP_N,
    TOP_N_MIN,
    TOP_N_MAX,
    TOP_N_STEP,
    CHART_HEIGHT_MAP,
    CHART_HEIGHT_BAR,
    CHART_HEIGHT_IMBALANCE,
    CHART_HEIGHT_LEISURE,
    MAP_TILE_STYLE,
    REGIONS,
    COLORS,
)
import plotly.graph_objects as go
from components.chart_card import chart_card
from components.station_inspector import render_station_inspector
from components.dispatch_panel import render_dispatch_panel


try:
    _MAP_TRACE = go.Scattermap
    _MAP_LAYOUT_KEY = "map"
except AttributeError:
    _MAP_TRACE = go.Scattermapbox
    _MAP_LAYOUT_KEY = "mapbox"


def _initial_map_figure() -> go.Figure:
    """Create a blank Mapbox figure centered on SF to eliminate Cartesian 0-6 axes flash during loading."""
    fig = go.Figure()
    fig.add_trace(
        _MAP_TRACE(
            lat=[37.776],
            lon=[-122.416],
            mode="markers",
            marker=dict(size=0.1, opacity=0),
            hoverinfo="none",
            showlegend=False,
        )
    )
    fig.update_layout(
        **{_MAP_LAYOUT_KEY: {
            "style": MAP_TILE_STYLE,
            "center": REGIONS["All"]["center"],
            "zoom": REGIONS["All"]["zoom"],
        }},
        paper_bgcolor=COLORS["bg_card"],
        plot_bgcolor=COLORS["bg_card"],
        height=CHART_HEIGHT_MAP,
        margin=dict(r=0, t=0, l=0, b=0),
        showlegend=False,
    )
    return fig


def _map_floating_legend() -> html.Details:
    """Integrated Floating Map Legend matching the high-end reference platform (collapsible)."""
    return html.Details(
        open=True,
        className="station-map-legend absolute bottom-4 left-4 z-40 bg-white/95 backdrop-blur-md border border-slate-200/90 shadow-xl rounded-xl text-xs w-[310px] pointer-events-auto transition-all group select-none",
        children=[
            html.Summary(
                className="font-bold text-slate-800 p-3.5 flex justify-between items-center cursor-pointer list-none outline-none border-b border-slate-100",
                children=[
                    html.Div([
                        html.I(className="fas fa-layer-group text-teal-600 mr-1.5"),
                        html.Span("Map Legend", className="tracking-wide text-xs font-bold"),
                    ], className="flex items-center"),
                    html.Div([
                        html.Span(
                            "Click station for profile",
                            className="text-[10px] text-teal-600 font-medium bg-teal-50 px-2 py-0.5 rounded border border-teal-200/50 mr-2",
                        ),
                        html.I(className="fas fa-chevron-down text-slate-400 text-xs transition-transform group-open:rotate-180"),
                    ], className="flex items-center"),
                ],
            ),
            html.Div(
                className="p-3.5 pt-2.5",
                children=[
                    # Net Flow Imbalance Gradient
                    html.Div(
                        className="mb-3",
                        children=[
                            html.Span(
                                "Net Flow Imbalance (Inbound − Outbound)",
                                className="block text-[11px] font-semibold text-slate-700 mb-1.5",
                            ),
                            html.Div(
                                style={
                                    "height": "8px",
                                    "width": "100%",
                                    "borderRadius": "999px",
                                    "background": "linear-gradient(to right, #F97316 0%, #94A3B8 50%, #3B82F6 100%)",
                                    "marginBottom": "4px",
                                    "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.15)",
                                }
                            ),
                            html.Div(
                                className="grid grid-cols-3 text-[10px] items-center pt-0.5",
                                children=[
                                    html.Div([
                                        html.Span("◄ Deficit", className="text-orange-600 font-bold block"),
                                        html.Span("(Outbound)", className="text-[9px] text-slate-400 block"),
                                    ], className="text-left"),
                                    html.Div([
                                        html.Span("Balanced", className="text-slate-500 font-semibold block"),
                                        html.Span("(Net ~0)", className="text-[9px] text-slate-400 block"),
                                    ], className="text-center"),
                                    html.Div([
                                        html.Span("Surplus ►", className="text-blue-600 font-bold block"),
                                        html.Span("(Inbound)", className="text-[9px] text-slate-400 block"),
                                    ], className="text-right"),
                                ],
                            ),
                        ],
                    ),
                    # Circle Size Meaning
                    html.Div(
                        className="mb-2",
                        children=[
                            html.Span(
                                "Total Trip Volume (Circle Radius)",
                                className="block text-[11px] font-semibold text-slate-700 mb-1.5",
                            ),
                            html.Div(
                                className="flex items-center justify-between text-[10px] text-slate-600 pt-0.5 px-1",
                                children=[
                                    html.Div([
                                        html.Span(className="w-2 h-2 rounded-full bg-teal-500/70 border border-teal-600 inline-block mr-1.5"),
                                        html.Span("< 5k trips"),
                                    ], className="flex items-center"),
                                    html.Div([
                                        html.Span(className="w-3.5 h-3.5 rounded-full bg-teal-500/80 border border-teal-600 inline-block mr-1.5"),
                                        html.Span("15k trips"),
                                    ], className="flex items-center"),
                                    html.Div([
                                        html.Span(className="w-5 h-5 rounded-full bg-teal-500 border border-teal-600 inline-block mr-1.5 shadow-xs shadow-teal-500/40"),
                                        html.Span("35k+ trips"),
                                    ], className="flex items-center font-semibold"),
                                ],
                            ),
                        ],
                    ),
                    # Corridor line item
                    html.Div(
                        className="pt-2 border-t border-slate-100 flex items-center gap-2",
                        children=[
                            html.Span(className="w-6 h-1 bg-gradient-to-r from-teal-400 to-teal-600 rounded-full inline-block shadow-xs shadow-teal-500/50"),
                            html.Span("Transit Corridor Vector (Width ∝ Commuter Volume)", className="text-[10px] text-slate-600 font-medium"),
                        ],
                    ),
                ],
            ),
        ],
    )


def create_layout() -> html.Div:
    """
    Construct the full Station & Trip Analysis section layout matching station_trip_analysis.html.
    """
    return html.Div(
        className="w-full flex flex-col gap-6",
        children=[
            # State store for clicked station across map and charts
            dcc.Store(id=ID_SELECTED_STATION_STORE, data=None),

            # Hidden sub-module filter controls (bridged seamlessly from Global Filter Bar)
            html.Div(
                style={"display": "none"},
                children=[
                    dcc.Dropdown(
                        id=ID_USER_FILTER,
                        options=[
                            {"label": "All Users", "value": "All"},
                            {"label": "Subscriber", "value": "Subscriber"},
                            {"label": "Casual", "value": "Customer"},
                        ],
                        value="All",
                    ),
                    dcc.Dropdown(
                        id=ID_REGION_FILTER,
                        options=[
                            {"label": "All Bay Area", "value": "All"},
                            {"label": "San Francisco", "value": "San Francisco"},
                            {"label": "East Bay", "value": "East Bay (Oakland/Berkeley)"},
                            {"label": "San Jose", "value": "San Jose"},
                        ],
                        value="All",
                    ),
                    dcc.Dropdown(
                        id="m5-gender-filter",
                        options=[
                            {"label": "All Genders", "value": "All"},
                            {"label": "Male", "value": "Male"},
                            {"label": "Female", "value": "Female"},
                            {"label": "Other", "value": "Other"},
                        ],
                        value="All",
                    ),
                    dcc.Dropdown(
                        id="m5-day-filter",
                        options=[
                            {"label": "All Days", "value": "All"},
                            {"label": "Weekday", "value": "Weekday"},
                            {"label": "Weekend", "value": "Weekend"},
                        ],
                        value="All",
                    ),
                ],
            ),

            # ── 1. Top Controls Bar: Top-N Slider & Map Toggles ──────────────────
            html.Section(
                className="analytics-card p-4 flex flex-wrap items-center justify-between gap-4 bg-white rounded-xl border border-slate-200/90 shadow-2xs",
                children=[
                    # Left: Top-N Rankings Display Slider
                    html.Div(
                        className="flex items-center gap-3",
                        children=[
                            html.Span("Top-N Rankings Display:", className="text-xs font-bold text-slate-800"),
                            html.Div(
                                style={"width": "150px"},
                                children=[
                                    dcc.Slider(
                                        id=ID_TOP_N_SLIDER,
                                        min=TOP_N_MIN,
                                        max=TOP_N_MAX,
                                        step=TOP_N_STEP,
                                        value=DEFAULT_TOP_N,
                                        marks={5: "5", 10: "10", 20: "20", 30: "30"},
                                        tooltip={"placement": "bottom", "always_visible": False},
                                    ),
                                ],
                            ),
                            html.Span(
                                f"Top {DEFAULT_TOP_N}",
                                id="m5-slider-scope-badge",
                                className="text-xs font-bold px-2 py-0.5 rounded-md bg-teal-50 text-teal-800 border border-teal-200",
                            ),
                        ],
                    ),

                    # Right: Corridor vectors toggle + Fit Entire Bay Area + Export CSV
                    html.Div(
                        className="flex items-center gap-4",
                        children=[
                            dcc.Checklist(
                                id=ID_MAP_FLOW_LINES_TOGGLE,
                                options=[
                                    {"label": " Display Major Transit Corridor Vectors", "value": "show"},
                                ],
                                value=["show"],
                                className="text-xs font-medium text-slate-700 cursor-pointer",
                            ),
                            html.Span("|", className="text-slate-300"),
                            html.Button(
                                [
                                    html.I(className="fas fa-crosshairs text-xs mr-1 text-slate-400"),
                                    html.Span("Fit Entire Bay Area"),
                                ],
                                id="m5-fit-bay-btn",
                                className="text-xs font-medium text-slate-500 hover:text-slate-800 flex items-center bg-transparent border-0 cursor-pointer",
                                n_clicks=0,
                            ),
                            html.Button(
                                [
                                    html.I(className="fas fa-download text-xs mr-1.5"),
                                    html.Span("Export CSV"),
                                ],
                                id=ID_DOWNLOAD_BTN,
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer",
                                n_clicks=0,
                            ),
                            dcc.Download(id=ID_DOWNLOAD_DATA),
                        ],
                    ),
                ],
            ),

            # ── 2. Station Traffic & Flow Corridor Map (Full Width with Drawer) ──
            html.Div(
                className="analytics-card p-0 relative overflow-hidden border border-slate-200/90 rounded-xl shadow-2xs",
                children=[
                    html.Div(
                        style={
                            "position": "relative",
                            "width": "100%",
                            "height": f"{CHART_HEIGHT_MAP}px",
                            "borderRadius": "12px",
                            "overflow": "hidden",
                        },
                        children=[
                            dcc.Loading(
                                id="m5-map-loading",
                                type="dot",
                                color="#14B8A6",
                                children=[
                                    dcc.Graph(
                                        id=ID_MAP,
                                        figure=_initial_map_figure(),
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
                                ],
                            ),
                            # Integrated Floating Map Legend
                            _map_floating_legend(),
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

            # ── 3. Two-Column Analytical Charts: Volume & Corridors ──────────────
            html.Div(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start",
                children=[
                    chart_card(
                        graph_id=ID_TOP_STATIONS,
                        title="Top Stations by Total Traffic",
                        subtitle="Total trip departures and arrivals combined across active network slice.",
                        badge_text="Total Rides",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600",
                        footnote="* Hover bars to see unshortened station names and exact network proportions",
                        height=CHART_HEIGHT_BAR,
                    ),
                    chart_card(
                        graph_id=ID_TOP_ROUTES,
                        title="Top Origin → Destination Corridors",
                        subtitle="Highest-density directional point-to-point commuter pathways.",
                        badge_text="Directional Flow",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-teal-100 text-teal-800",
                        footnote="* Arrows indicate origin station to terminal destination station",
                        height=CHART_HEIGHT_BAR,
                    ),
                ],
            ),

            # ── 4. Two-Column Analytical Charts: Imbalance & Leisure ─────────────
            html.Div(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start",
                children=[
                    chart_card(
                        graph_id=ID_FLOW_IMBALANCE,
                        title="Network Flow Imbalance (Diverging)",
                        subtitle="Red = Net Deficit (Out > In, Needs Bikes), Blue = Net Surplus (In > Out, Needs Docks).",
                        badges=[
                            html.Span("Deficit (-)", className="text-orange-600 bg-orange-50 px-2 py-0.5 rounded border border-orange-200 text-[10px] font-bold"),
                            html.Span("Surplus (+)", className="text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 text-[10px] font-bold"),
                        ],
                        footnote_left="Orange: Bike re-stocking needed",
                        footnote="Blue: Bike clearance needed",
                        height=CHART_HEIGHT_IMBALANCE,
                    ),
                    chart_card(
                        graph_id=ID_ROUND_TRIP_CHART,
                        title="Leisure & Tourism Hotspots",
                        subtitle="Highest percentage of round-trip loops (Origin == Destination) signaling recreational riding.",
                        badge_text="Min 100 Departures",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-purple-100 text-purple-800",
                        footnote="* Filtered for stations with ≥100 departures to eliminate small-sample bias",
                        height=CHART_HEIGHT_LEISURE,
                    ),
                ],
            ),

            # ── 5. Prescriptive Fleet Dispatch & Rebalancing ────────────────────
            html.Div(
                children=[
                    html.Div(
                        id=ID_DISPATCH_CONTAINER,
                        children=render_dispatch_panel([]),
                    ),
                ],
            ),
        ],
    )
