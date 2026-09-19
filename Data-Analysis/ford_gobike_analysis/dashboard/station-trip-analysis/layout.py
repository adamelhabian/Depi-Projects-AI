"""
layout.py – Section Layout for Member 5: Station & Trip Analysis
================================================================
Tailwind CSS-driven layout with an integrated sticky Sidebar navigation:

  - Full-width Header (title + live status pill + mobile hamburger)
  - Global Filter Panel wrapped in a dedicated div so it can be
    shown ONLY while the Station Analysis section is active
  - Flex row: [Sticky Sidebar (desktop)] + [Main Content Sections]
  - Main content is split into 4 switchable sections:
      * Station Analysis (map + top stations + top routes + flow + leisure)
      * Time Analysis (4 charts)
      * User Analysis (6 charts)
      * Fleet Dispatch (rebalancing panel)
  - Mobile drawer + backdrop rendered alongside the main content
"""

from __future__ import annotations

from dash import dcc, html

from config import (
    # Charts
    ID_MAP,
    ID_TOP_STATIONS,
    ID_TOP_ROUTES,
    ID_FLOW_IMBALANCE,
    ID_ROUND_TRIP_CHART,
    ID_TRIPS_BY_HOUR,
    ID_DAY_HOUR_HEATMAP,
    ID_AVG_DURATION_BY_HOUR,
    ID_WEEKDAY_WEEKEND_DURATION,
    ID_USER_TYPE_DISTRIBUTION,
    ID_USER_TYPE_HOUR,
    ID_AVG_DURATION_BY_USER_TYPE,
    ID_AGE_GROUP_DISTRIBUTION,
    ID_GENDER_DISTRIBUTION,
    ID_USER_TYPE_BY_AGE_GROUP,

    # Containers & stores
    ID_INSPECTOR_CONTAINER,
    ID_DISPATCH_CONTAINER,
    ID_SELECTED_STATION_STORE,

    # Sidebar
    ID_ACTIVE_SECTION_STORE,
    ID_ACTIVE_ANCHOR_STORE,
    ID_MOBILE_MENU_STORE,
    ID_MOBILE_MENU_TOGGLE,
    ID_SECTION_STATION,
    ID_SECTION_TIME,
    ID_SECTION_USER,
    ID_SECTION_DISPATCH,
    ID_FILTER_PANEL_WRAPPER,
    DEFAULT_ACTIVE_SECTION,

    # Chart heights
    CHART_HEIGHT_MAP,
    CHART_HEIGHT_BAR,
    CHART_HEIGHT_IMBALANCE,
    CHART_HEIGHT_LEISURE,
    CHART_HEIGHT_LINE,
    CHART_HEIGHT_HEATMAP,
)
from components.chart_card import chart_card
from components.filter_panel import filter_panel
from components.sidebar import sidebar, mobile_sidebar
from components.station_inspector import render_station_inspector
from components.dispatch_panel import render_dispatch_panel


# ---------------------------------------------------------------------------
# Anchor group IDs — used by clientside scroll callback
# ---------------------------------------------------------------------------
ANCHOR_GROUP_STATION_NETWORK = "m5-anchor-station-network-group"
ANCHOR_GROUP_STATION_TRAFFIC = "m5-anchor-station-traffic-group"
ANCHOR_GROUP_STATION_FLOW    = "m5-anchor-station-flow-group"

ANCHOR_GROUP_TIME_HOURLY     = "m5-anchor-time-hourly-group"
ANCHOR_GROUP_TIME_DAYHOUR    = "m5-anchor-time-dayhour-group"
ANCHOR_GROUP_TIME_DURATION   = "m5-anchor-time-duration-group"

ANCHOR_GROUP_USER_TYPE       = "m5-anchor-user-type-group"
ANCHOR_GROUP_USER_DEMO       = "m5-anchor-user-demographics-group"
ANCHOR_GROUP_USER_CROSSTAB   = "m5-anchor-user-crosstab-group"

ANCHOR_GROUP_DISPATCH_PLAN   = "m5-anchor-dispatch-plan-group"


# ---------------------------------------------------------------------------
# Map floating legend
# ---------------------------------------------------------------------------
def _map_floating_legend() -> html.Div:
    """Integrated Floating Map Legend matching station_trip_analysis.html."""
    return html.Div(
        className="absolute bottom-4 left-4 z-40 bg-white/95 backdrop-blur-sm border border-slate-200 shadow-lg rounded-xl p-3 text-xs max-w-[280px] pointer-events-auto",
        children=[
            html.Div(
                className="font-bold text-slate-800 mb-2 border-b border-slate-100 pb-1 flex justify-between items-center",
                children=[
                    html.Span("Map Legend"),
                    html.Span("Click station for profile", className="text-[10px] text-slate-400 font-normal"),
                ],
            ),
            html.Div(
                className="mb-2.5",
                children=[
                    html.Span("Net Flow Imbalance (Inbound - Outbound)", className="block text-[11px] font-semibold text-slate-600 mb-1"),
                    html.Div(
                        style={
                            "height": "10px",
                            "width": "100%",
                            "borderRadius": "999px",
                            "background": "linear-gradient(to right, #f43f5e, #94a3b8, #10b981)",
                            "marginBottom": "4px",
                        }
                    ),
                    html.Div(
                        className="flex justify-between text-[10px] text-slate-500 font-medium",
                        children=[
                            html.Span("◄ Deficit (Outbound)", className="text-pink-600 font-bold"),
                            html.Span("Balanced"),
                            html.Span("Surplus (Inbound) ►", className="text-emerald-600 font-bold"),
                        ],
                    ),
                ],
            ),
            html.Div(
                children=[
                    html.Span("Total Trip Volume (Circle Radius)", className="block text-[11px] font-semibold text-slate-600 mb-1"),
                    html.Div(
                        className="flex items-center justify-between text-[10px] text-slate-600 pt-0.5",
                        children=[
                            html.Div([
                                html.Span(className="w-2.5 h-2.5 rounded-full border border-slate-400 bg-slate-300 inline-block mr-1"),
                                html.Span("< 5k trips"),
                            ], className="flex items-center"),
                            html.Div([
                                html.Span(className="w-4 h-4 rounded-full border border-slate-400 bg-slate-300 inline-block mr-1"),
                                html.Span("15k trips"),
                            ], className="flex items-center"),
                            html.Div([
                                html.Span(className="w-6 h-6 rounded-full border border-slate-400 bg-slate-300 inline-block mr-1"),
                                html.Span("35k+"),
                            ], className="flex items-center"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="mt-2 pt-1.5 border-t border-slate-100 flex items-center gap-2",
                children=[
                    html.Span(className="w-5 h-1 bg-teal-600 rounded inline-block"),
                    html.Span("Top Corridor Volume (Line Width)", className="text-[10px] text-slate-600"),
                ],
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Section sub-header
# ---------------------------------------------------------------------------
def _section_header(title: str, subtitle: str, badge: str) -> html.Div:
    return html.Div(
        className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-200",
        children=[
            html.Div([
                html.H2(title, className="text-lg font-bold text-slate-900 tracking-tight"),
                html.P(subtitle, className="text-xs text-slate-500 mt-0.5"),
            ]),
            html.Div(
                className="flex items-center gap-2 text-xs font-medium",
                children=[
                    html.Span(
                        badge,
                        className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 shadow-sm text-slate-500",
                    ),
                ],
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Section 1: Station Analysis
# ---------------------------------------------------------------------------
def _section_station() -> html.Div:
    return html.Div(
        id=ID_SECTION_STATION,
        style={"display": "block"},  # active by default
        className="m5-section",
        children=[
            _section_header(
                title="Station Analysis",
                subtitle="Network traffic hubs, corridor flows, spatial rebalancing, and station deep dives.",
                badge="Network Overview · Traffic · Flow",
            ),

            # Map — anchor target for "Network Overview"
            html.Div(
                id=ANCHOR_GROUP_STATION_NETWORK,
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
                                    "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
                                },
                            ),
                            _map_floating_legend(),
                            html.Div(
                                id=ID_INSPECTOR_CONTAINER,
                                className="station-drawer drawer-closed",
                                children=render_station_inspector(None),
                            ),
                        ],
                    ),
                ],
            ),

            # Row: Top Stations + Top Routes — anchor target for "Station Traffic"
            html.Div(
                id=ANCHOR_GROUP_STATION_TRAFFIC,
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6 items-start",
                children=[
                    chart_card(
                        graph_id=ID_TOP_STATIONS,
                        title="Top Stations by Total Traffic",
                        subtitle="Ranking stations by cumulative arrivals and departures. Percentages reflect share of active network traffic.",
                        badge_text="Total Rides",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600",
                        footnote="* Hover bars to see unshortened station names and exact network proportions",
                        height=CHART_HEIGHT_BAR,
                    ),
                    chart_card(
                        graph_id=ID_TOP_ROUTES,
                        title="Top Origin–Destination Corridors",
                        subtitle="Highest volume point-to-point station pairs across the network.",
                        badge_text="Directional Flow",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-teal-100 text-teal-800",
                        footnote="* Arrows indicate origin station to terminal destination station",
                        height=CHART_HEIGHT_BAR,
                    ),
                ],
            ),

            # Row: Flow Imbalance + Round Trip — anchor target for "Flow Analysis"
            html.Div(
                id=ANCHOR_GROUP_STATION_FLOW,
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6 items-start",
                children=[
                    chart_card(
                        graph_id=ID_FLOW_IMBALANCE,
                        title="Station Network Flow Imbalance",
                        subtitle="Critical stations demanding truck/van rebalancing. Identifies dock depletion vs overflow docks.",
                        badges=[
                            html.Span("Outbound Deficit (-)", className="text-pink-600 bg-pink-50 px-2 py-0.5 rounded border border-pink-200 text-[10px] font-bold"),
                            html.Span("Inbound Surplus (+)", className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 text-[10px] font-bold"),
                        ],
                        footnote_left="Pink: Bike re-stocking needed",
                        footnote="Green: Bike clearance needed",
                        height=CHART_HEIGHT_IMBALANCE,
                    ),
                    chart_card(
                        graph_id=ID_ROUND_TRIP_CHART,
                        title="Leisure & Tourism Hotspots",
                        subtitle="Stations exhibiting high percentages of loop journeys (origin = destination), signaling recreational riding.",
                        badge_text="Round-Trip Ratio",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-purple-100 text-purple-800",
                        footnote="* Percentage represents the station's own round-trip ratio, not share of overall network",
                        height=CHART_HEIGHT_LEISURE,
                    ),
                ],
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Section 2: Time Analysis
# ---------------------------------------------------------------------------
def _section_time() -> html.Div:
    return html.Div(
        id=ID_SECTION_TIME,
        style={"display": "none"},
        className="m5-section",
        children=[
            _section_header(
                title="Time Analysis",
                subtitle="Temporal demand patterns, hourly usage concentration, and trip duration profiles across the network.",
                badge="Hourly · Day-of-Week · Weekday vs Weekend",
            ),

            html.Div(
                id=ANCHOR_GROUP_TIME_HOURLY,
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6 items-start",
                children=[
                    chart_card(
                        graph_id=ID_TRIPS_BY_HOUR,
                        title="Trips by Hour of Day",
                        subtitle="Total trips recorded per hour. Peak hours are detected dynamically from the active filter scope.",
                        badge_text="Demand Curve",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-teal-100 text-teal-800",
                        footnote="* Hour axis runs 00:00 → 23:00 in local time",
                        height=CHART_HEIGHT_LINE,
                    ),
                    chart_card(
                        graph_id=ID_AVG_DURATION_BY_HOUR,
                        title="Average Trip Duration by Hour",
                        subtitle="Mean trip duration (minutes) per start hour. Highlights off-peak periods with longer rides.",
                        badge_text="Duration Profile",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-purple-100 text-purple-800",
                        footnote="* Hours with no recorded trips are omitted from the line",
                        height=CHART_HEIGHT_LINE,
                    ),
                ],
            ),

            html.Div(
                id=ANCHOR_GROUP_TIME_DAYHOUR,
                className="mb-6",
                children=[
                    chart_card(
                        graph_id=ID_DAY_HOUR_HEATMAP,
                        title="Day-of-Week × Hour Heatmap",
                        subtitle="Demand intensity matrix across the week. Darker cells indicate higher trip concentration.",
                        badge_text="Demand Matrix",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800",
                        footnote="* Rows follow Monday → Sunday; columns follow 00:00 → 23:00",
                        height=CHART_HEIGHT_HEATMAP,
                    ),
                ],
            ),

            html.Div(
                id=ANCHOR_GROUP_TIME_DURATION,
                className="mb-6",
                children=[
                    chart_card(
                        graph_id=ID_WEEKDAY_WEEKEND_DURATION,
                        title="Weekday vs Weekend Average Duration",
                        subtitle="Mean trip duration comparison between working days and weekend riding patterns.",
                        badge_text="Day Type Comparison",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600",
                        footnote="* Uses the dataset's weekend flag; both boolean and 0/1 encodings are supported",
                        height=CHART_HEIGHT_LINE,
                    ),
                ],
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Section 3: User Analysis
# ---------------------------------------------------------------------------
def _section_user() -> html.Div:
    return html.Div(
        id=ID_SECTION_USER,
        style={"display": "none"},
        className="m5-section",
        children=[
            _section_header(
                title="User Analysis",
                subtitle="User-type composition, hourly behavior, duration profiles, and demographic distributions across the network.",
                badge="User Type · Age · Gender",
            ),

            html.Div(
                id=ANCHOR_GROUP_USER_TYPE,
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6 items-start",
                children=[
                    chart_card(
                        graph_id=ID_USER_TYPE_DISTRIBUTION,
                        title="User Type Distribution",
                        subtitle="Share of trips between Subscriber and Customer user types across the active filter scope.",
                        badge_text="Composition",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-teal-100 text-teal-800",
                        footnote="* Donut segments are proportional to total trips per user type",
                        height=CHART_HEIGHT_BAR,
                    ),
                    chart_card(
                        graph_id=ID_USER_TYPE_HOUR,
                        title="Hourly Usage Pattern by User Type",
                        subtitle="Normalized hourly distribution within each user type, enabling direct pattern comparison.",
                        badge_text="Hourly Pattern",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-purple-100 text-purple-800",
                        footnote="* Each curve sums to 100% of that user type's total trips",
                        height=CHART_HEIGHT_LINE,
                    ),
                ],
            ),

            html.Div(
                id=ANCHOR_GROUP_USER_DEMO,
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6 items-start",
                children=[
                    chart_card(
                        graph_id=ID_AVG_DURATION_BY_USER_TYPE,
                        title="Average Trip Duration by User Type",
                        subtitle="Mean trip duration comparison between Subscriber and Customer users.",
                        badge_text="Duration Comparison",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-teal-100 text-teal-800",
                        footnote="* Bars reflect mean duration in minutes after filtering",
                        height=CHART_HEIGHT_BAR,
                    ),
                    chart_card(
                        graph_id=ID_AGE_GROUP_DISTRIBUTION,
                        title="Trip Distribution by Age Group",
                        subtitle="Trip counts across age bands derived from rider birth-year records.",
                        badge_text="Age Cohorts",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-amber-100 text-amber-800",
                        footnote="* Age groups: 18-25 · 26-35 · 36-50 · 51-65 · 66-80",
                        height=CHART_HEIGHT_BAR,
                    ),
                ],
            ),

            html.Div(
                id=ANCHOR_GROUP_USER_CROSSTAB,
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start",
                children=[
                    chart_card(
                        graph_id=ID_GENDER_DISTRIBUTION,
                        title="Gender Distribution",
                        subtitle="Share of trips across member gender categories reported in the trip ledger.",
                        badge_text="Demographics",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-purple-100 text-purple-800",
                        footnote="* Categories reflect the source dataset's member_gender field",
                        height=CHART_HEIGHT_BAR,
                    ),
                    chart_card(
                        graph_id=ID_USER_TYPE_BY_AGE_GROUP,
                        title="User Type Distribution Across Age Groups",
                        subtitle="100% stacked comparison of Subscriber vs Customer composition inside each age band.",
                        badge_text="Cross-Tab",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600",
                        footnote="* Each bar sums to 100% of trips within that age group",
                        height=CHART_HEIGHT_BAR,
                    ),
                ],
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Section 4: Fleet Dispatch
# ---------------------------------------------------------------------------
def _section_dispatch() -> html.Div:
    return html.Div(
        id=ID_SECTION_DISPATCH,
        style={"display": "none"},
        className="m5-section",
        children=[
            _section_header(
                title="Prescriptive Fleet Dispatch",
                subtitle="Rebalancing recommendations derived from station-level net flow imbalance across the active network.",
                badge="Operational Recommendations",
            ),
            html.Div(
                id=ANCHOR_GROUP_DISPATCH_PLAN,
                children=[
                    html.Div(
                        id=ID_DISPATCH_CONTAINER,
                        children=render_dispatch_panel([]),
                    ),
                ],
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Mobile hamburger
# ---------------------------------------------------------------------------
def _mobile_hamburger() -> html.Button:
    return html.Button(
        [
            html.Span("☰", className="text-xl leading-none"),
        ],
        id=ID_MOBILE_MENU_TOGGLE,
        n_clicks=0,
        className=(
            "lg:hidden inline-flex items-center justify-center "
            "w-10 h-10 rounded-lg bg-white border border-slate-200 shadow-sm "
            "text-slate-700 hover:bg-slate-50 transition active:scale-95 cursor-pointer"
        ),
        **{"aria-label": "Toggle navigation menu"},
    )


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
def create_layout() -> html.Div:
    """
    Construct the full Station & Trip Analysis layout with an integrated
    sticky Sidebar navigation and a section-scoped Global Filter Panel.
    """
    return html.Div(
        className="w-full",
        children=[
            # ── Global state stores ─────────────────────────────────────
            dcc.Store(id=ID_SELECTED_STATION_STORE, data=None),
            dcc.Store(id=ID_ACTIVE_SECTION_STORE, data=DEFAULT_ACTIVE_SECTION),
            dcc.Store(id=ID_ACTIVE_ANCHOR_STORE, data=None),
            dcc.Store(id=ID_MOBILE_MENU_STORE, data=False),

            # ── Header (full width) ─────────────────────────────────────
            html.Header(
                className="mb-6",
                children=[
                    html.Div(
                        className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-200",
                        children=[
                            html.Div(
                                className="flex items-center gap-3",
                                children=[
                                    _mobile_hamburger(),
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
                                ],
                            ),
                            html.Div(
                                className="flex items-center gap-2 text-xs font-medium",
                                children=[
                                    html.Span(
                                        [
                                            html.Span(className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse inline-block mr-2"),
                                            "LIVE: Supabase Cloud",
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

            # ── Filter Panel Wrapper (visible only on Station Analysis) ─
            html.Div(
                id=ID_FILTER_PANEL_WRAPPER,
                style={"display": "block"},
                children=[filter_panel()],
            ),

            # ── Body: Sidebar + Main Content ────────────────────────────
            html.Div(
                className="flex gap-6 items-start",
                children=[
                    sidebar(),

                    html.Main(
                        className="flex-1 min-w-0",
                        children=[
                            _section_station(),
                            _section_time(),
                            _section_user(),
                            _section_dispatch(),
                        ],
                    ),
                ],
            ),

            # ── Mobile drawer + backdrop ────────────────────────────────
            *mobile_sidebar(),
        ],
    )