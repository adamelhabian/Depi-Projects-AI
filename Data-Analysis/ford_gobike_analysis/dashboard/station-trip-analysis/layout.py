"""
layout.py – Section Layout for Member 5: Station & Trip Analysis
================================================================
Tailwind CSS-driven layout perfectly matching station_trip_analysis.html:
  1. Section Header with Bay Wheels system badge, title, and live Supabase pulse pill.
  2. 12-Column Responsive Controls Bar (Membership, Region, Top N Slider, Export).
  3. Interactive Map with integrated Floating Map Legend and Slide-in Side Drawer.
  4. Top Stations by Total Traffic & Top Origin–Destination Corridors (side-by-side).
  5. Station Network Flow Imbalance & Leisure & Tourism Hotspots (side-by-side).
  6. Time Analysis: Hourly demand, duration profiles, day×hour heatmap,
     and weekday/weekend comparison.
  7. User Analysis: User-type composition, hourly patterns, duration profiles,
     age/gender distributions, and cross-tab user-type × age.
  8. Prescriptive Fleet Dispatch & Rebalancing Panel.
"""

from __future__ import annotations

from dash import dcc, html

from config import (
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
    ID_INSPECTOR_CONTAINER,
    ID_DISPATCH_CONTAINER,
    ID_SELECTED_STATION_STORE,
    CHART_HEIGHT_MAP,
    CHART_HEIGHT_BAR,
    CHART_HEIGHT_IMBALANCE,
    CHART_HEIGHT_LEISURE,
    CHART_HEIGHT_LINE,
    CHART_HEIGHT_HEATMAP,
)
from components.chart_card import chart_card
from components.filter_panel import filter_panel
from components.station_inspector import render_station_inspector
from components.dispatch_panel import render_dispatch_panel


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
            # Net Flow Imbalance Gradient
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
            # Circle Size Meaning
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
            # Corridor line item
            html.Div(
                className="mt-2 pt-1.5 border-t border-slate-100 flex items-center gap-2",
                children=[
                    html.Span(className="w-5 h-1 bg-teal-600 rounded inline-block"),
                    html.Span("Top Corridor Volume (Line Width)", className="text-[10px] text-slate-600"),
                ],
            ),
        ],
    )


def create_layout() -> html.Div:
    """
    Construct the full Station & Trip Analysis section layout matching station_trip_analysis.html.
    """
    return html.Div(
        className="w-full",
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

            # ── 4. Two-Column Analytical Charts: Volume & Corridors ──────
            html.Div(
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

            # ── 5. Two-Column Analytical Charts: Imbalance & Leisure ─────
            html.Div(
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

            # ── 6. Time Analysis (Temporal Usage & Duration) ─────────────
            html.Div(
                className="mb-6",
                children=[
                    # Section sub-header (matches Section 1 header style, smaller scale)
                    html.Div(
                        className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-200",
                        children=[
                            html.Div([
                                html.H2(
                                    "Time Analysis",
                                    className="text-lg font-bold text-slate-900 tracking-tight",
                                ),
                                html.P(
                                    "Temporal demand patterns, hourly usage concentration, and trip duration profiles across the network.",
                                    className="text-xs text-slate-500 mt-0.5",
                                ),
                            ]),
                            html.Div(
                                className="flex items-center gap-2 text-xs font-medium",
                                children=[
                                    html.Span(
                                        "Hourly · Day-of-Week · Weekday vs Weekend",
                                        className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 shadow-sm text-slate-500",
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Row 1 — Trips by Hour + Avg Duration by Hour
                    html.Div(
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

                    # Row 2 — Day × Hour Heatmap (Full width)
                    chart_card(
                        graph_id=ID_DAY_HOUR_HEATMAP,
                        title="Day-of-Week × Hour Heatmap",
                        subtitle="Demand intensity matrix across the week. Darker cells indicate higher trip concentration.",
                        badge_text="Demand Matrix",
                        badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800",
                        footnote="* Rows follow Monday → Sunday; columns follow 00:00 → 23:00",
                        height=CHART_HEIGHT_HEATMAP,
                    ),

                    # Row 3 — Weekday vs Weekend (Full width)
                    html.Div(
                        className="mt-6",
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
            ),

            # ── 7. User Analysis (Behavior & Demographics) ───────────────
            html.Div(
                className="mb-6",
                children=[
                    # Section sub-header
                    html.Div(
                        className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-200",
                        children=[
                            html.Div([
                                html.H2(
                                    "User Analysis",
                                    className="text-lg font-bold text-slate-900 tracking-tight",
                                ),
                                html.P(
                                    "User-type composition, hourly behavior, duration profiles, and demographic distributions across the network.",
                                    className="text-xs text-slate-500 mt-0.5",
                                ),
                            ]),
                            html.Div(
                                className="flex items-center gap-2 text-xs font-medium",
                                children=[
                                    html.Span(
                                        "User Type · Age · Gender",
                                        className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 shadow-sm text-slate-500",
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Row 1 — User Type Distribution + Hourly Pattern
                    html.Div(
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

                    # Row 2 — Avg Duration by User Type + Age Group Distribution
                    html.Div(
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

                    # Row 3 — Gender Distribution + User Type × Age Group
                    html.Div(
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
            ),

            # ── 8. Prescriptive Fleet Dispatch & Rebalancing ────────────
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