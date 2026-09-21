"""
layout.py – Clean SaaS Dashboard Layout for Time & Demographics Analysis
========================================================================
Tailwind CSS-driven layout perfectly matching Screenshots 2 & 3:
  - 4 Demographic Headline Metric Cards (Filtered Volume, Subscriber Ratio, Peak Commute, Avg Duration)
  - Exactly 5 Core Visualizations:
      * Row 1 (2 Charts): Hourly Demand (24h) & Day of Week Ridership Pattern
      * (Heatmap Matrix permanently excluded as requested)
      * Row 2 (3 Charts): Rider Membership Donut, Rider Age Demographics, Trip Duration Distribution
  - Zero duplicate headers or redundant filter panels (driven by sticky Global Filter Bar)
"""

from __future__ import annotations

from dash import dcc, html
from config import (
    # KPIs
    ID_KPI_TOTAL_TRIPS,
    ID_KPI_SUBSCRIBER_PCT,
    ID_KPI_PEAK_HOUR,
    ID_KPI_AVG_DURATION,
    # Filters
    ID_USER_FILTER,
    ID_DAY_FILTER,
    ID_GENDER_FILTER,
    ID_REGION_FILTER,
    # Charts
    ID_TRIPS_BY_HOUR,
    ID_TRIPS_BY_DAY,
    ID_USER_TYPE_DISTRIBUTION,
    ID_USER_TYPE_HOUR,
    ID_AGE_GROUP_DISTRIBUTION,
)

try:
    from utils.metrics_calculator import DEFAULT_KPIS
    SUB_DUR_STR = DEFAULT_KPIS["sub_duration_str"]
    CASUAL_DUR_STR = DEFAULT_KPIS["casual_duration_str"]
    RATIO_STR = DEFAULT_KPIS["duration_ratio_str"]
except ImportError:
    SUB_DUR_STR = "10.7m"
    CASUAL_DUR_STR = "21.7m"
    RATIO_STR = "2.0×"


def create_layout() -> html.Div:
    """Build the complete, modern Time & Demographics dashboard layout."""
    return html.Div(
        className="w-full flex flex-col gap-6",
        children=[
            # ── Hidden sub-module filter controls (bridged from Global Filter Bar) ──
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
                        id=ID_DAY_FILTER,
                        options=[
                            {"label": "All Days", "value": "All"},
                            {"label": "Weekday", "value": "Weekday"},
                            {"label": "Weekend", "value": "Weekend"},
                        ],
                        value="All",
                    ),
                    dcc.Dropdown(
                        id=ID_GENDER_FILTER,
                        options=[
                            {"label": "All Genders", "value": "All"},
                            {"label": "Male", "value": "Male"},
                            {"label": "Female", "value": "Female"},
                            {"label": "Other", "value": "Other"},
                        ],
                        value="All",
                    ),
                    dcc.Dropdown(
                        id=ID_REGION_FILTER,
                        options=[
                            {"label": "All Regions", "value": "All"},
                            {"label": "San Francisco", "value": "San Francisco"},
                            {"label": "East Bay (Oakland/Berkeley)", "value": "East Bay (Oakland/Berkeley)"},
                            {"label": "San Jose", "value": "San Jose"},
                        ],
                        value="All",
                    ),
                ],
            ),

            # ── 1. Headline 4 Demographic KPI Summary Cards ────────────────────────
            html.Section(
                className="grid grid-cols-2 lg:grid-cols-4 gap-4",
                children=[
                    # KPI 1: Filtered Volume
                    html.Div(
                        className="analytics-card p-4 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Span("Filtered Volume", className="text-xs font-medium text-slate-500"),
                            html.Div(
                                id=ID_KPI_TOTAL_TRIPS,
                                className="text-2xl font-black text-slate-900 tracking-tight my-1",
                                children="174,724",
                            ),
                            html.Span("100% Normalized Base", className="text-[11px] font-semibold text-teal-600"),
                        ],
                    ),

                    # KPI 2: Subscriber Ratio
                    html.Div(
                        className="analytics-card p-4 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Span("Subscriber Ratio", className="text-xs font-medium text-slate-500"),
                            html.Div(
                                id=ID_KPI_SUBSCRIBER_PCT,
                                className="text-2xl font-black text-teal-600 tracking-tight my-1",
                                children="90.5%",
                            ),
                            html.Span("Key commuter foundation", className="text-[11px] font-medium text-slate-400"),
                        ],
                    ),

                    # KPI 3: Peak Commute Windows
                    html.Div(
                        className="analytics-card p-4 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Span("Peak Commute Windows", className="text-xs font-medium text-slate-500"),
                            html.Div(
                                id=ID_KPI_PEAK_HOUR,
                                className="text-2xl font-black text-purple-600 tracking-tight my-1",
                                children="08:00 & 17:00",
                            ),
                            html.Span("Bimodal workday distribution", className="text-[11px] font-medium text-slate-400"),
                        ],
                    ),

                    # KPI 4: Average Trip Duration
                    html.Div(
                        className="analytics-card p-4 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Span("Average Trip Duration", className="text-xs font-medium text-slate-500"),
                            html.Div(
                                id=ID_KPI_AVG_DURATION,
                                className="text-2xl font-black text-slate-900 tracking-tight my-1",
                                children="11.7 min",
                            ),
                            html.Span(f"Subscribers: {SUB_DUR_STR} | Casual: {CASUAL_DUR_STR}", className="text-[11px] font-medium text-slate-400"),
                        ],
                    ),
                ],
            ),

            # ── 2. Row 1: Two Temporal Rhythm Charts ──────────────────────────────
            html.Section(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6",
                children=[
                    # Chart 1: Hourly Demand Profile
                    html.Div(
                        className="analytics-card p-5 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-2",
                                children=[
                                    html.Div([
                                        html.H3("Hourly Trip Demand (24-Hour Profile)", className="text-sm font-bold text-slate-900"),
                                        html.P("Annotated with overall daily average hourly demand reference line", className="text-xs text-slate-400 mt-0.5"),
                                    ]),
                                    html.Span(
                                        "Hourly Rhythm",
                                        className="text-[11px] font-bold text-teal-600 bg-teal-50 px-2 py-0.5 rounded",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="w-full",
                                children=[
                                    dcc.Graph(
                                        id=ID_TRIPS_BY_HOUR,
                                        config={"displayModeBar": False},
                                        style={"height": "340px", "width": "100%"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Chart 2: Day of Week Ridership Pattern
                    html.Div(
                        className="analytics-card p-5 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-2",
                                children=[
                                    html.Div([
                                        html.H3("Day of Week Ridership Pattern", className="text-sm font-bold text-slate-900"),
                                        html.P("Weekdays (Teal) vs Weekend recreational drop (Purple)", className="text-xs text-slate-400 mt-0.5"),
                                    ]),
                                    html.Span(
                                        "Weekly Volume",
                                        className="text-[11px] font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="w-full",
                                children=[
                                    dcc.Graph(
                                        id=ID_TRIPS_BY_DAY,
                                        config={"displayModeBar": False},
                                        style={"height": "340px", "width": "100%"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # ── 3. Row 2: Three Demographic & Behavioral Charts (Equal Height & Width) ──
            html.Section(
                className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6",
                children=[
                    # Chart 3: Rider Membership Split Donut
                    html.Div(
                        className="analytics-card p-5 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Div([
                                html.Div(
                                    className="flex items-center justify-between mb-1.5",
                                    children=[
                                        html.H3("Rider Membership Split", className="text-sm font-bold text-slate-900"),
                                        html.Span("90.5% Sub", className="text-[11px] font-bold text-teal-600 bg-teal-50 px-2 py-0.5 rounded"),
                                    ],
                                ),
                                html.P("Ratio of registered annual subscribers to single-trip casual guests", className="text-xs text-slate-400 mb-2"),
                                html.Div(
                                    dcc.Graph(
                                        id=ID_USER_TYPE_DISTRIBUTION,
                                        config={"displayModeBar": False},
                                        style={"height": "280px", "width": "100%"},
                                    ),
                                ),
                            ]),
                            html.Div(
                                className="flex items-center justify-around text-xs pt-3 border-t border-slate-100 text-slate-500",
                                children=[
                                    html.Div(
                                        className="flex items-center gap-1.5",
                                        children=[
                                            html.Span(className="w-2.5 h-2.5 rounded-full bg-teal-500 inline-block"),
                                            html.Span(["Subscriber: ", html.Strong("90.5%", className="text-slate-800")]),
                                        ],
                                    ),
                                    html.Div(
                                        className="flex items-center gap-1.5",
                                        children=[
                                            html.Span(className="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block"),
                                            html.Span(["Casual: ", html.Strong("9.5%", className="text-slate-800")]),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Chart 4: Rider Age Demographics
                    html.Div(
                        className="analytics-card p-5 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Div([
                                html.Div(
                                    className="flex items-center justify-between mb-1.5",
                                    children=[
                                        html.H3("Rider Age Demographics", className="text-sm font-bold text-slate-900"),
                                        html.Span("26–35 Core", className="text-[11px] font-bold text-teal-600 bg-teal-50 px-2 py-0.5 rounded"),
                                    ],
                                ),
                                html.P("Trip volume across standard demographic birth-year brackets", className="text-xs text-slate-400 mb-2"),
                                html.Div(
                                    dcc.Graph(
                                        id=ID_AGE_GROUP_DISTRIBUTION,
                                        config={"displayModeBar": False},
                                        style={"height": "280px", "width": "100%"},
                                    ),
                                ),
                            ]),
                            html.Div(
                                "Primary working-age group (26–35) accounts for ~47.4% of total network load.",
                                className="pt-3 border-t border-slate-100 text-[11px] text-slate-400 text-center font-medium",
                            ),
                        ],
                    ),

                    # Chart 5: Trip Duration Distribution
                    html.Div(
                        className="analytics-card p-5 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Div([
                                html.Div(
                                    className="flex items-center justify-between mb-1.5",
                                    children=[
                                        html.H3("Trip Duration Distribution", className="text-sm font-bold text-slate-900"),
                                        html.Span("11.7m Avg", className="text-[11px] font-bold text-teal-600 bg-teal-50 px-2 py-0.5 rounded"),
                                    ],
                                ),
                                html.P("Duration frequency split between subscriber and casual passes", className="text-xs text-slate-400 mb-2"),
                                html.Div(
                                    dcc.Graph(
                                        id=ID_USER_TYPE_HOUR,
                                        config={"displayModeBar": False},
                                        style={"height": "280px", "width": "100%"},
                                    ),
                                ),
                            ]),
                            html.Div(
                                f"Casual riders display {RATIO_STR} longer duration ({CASUAL_DUR_STR} vs {SUB_DUR_STR}) for recreational exploration.",
                                className="pt-3 border-t border-slate-100 text-[11px] text-slate-400 text-center font-medium",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )