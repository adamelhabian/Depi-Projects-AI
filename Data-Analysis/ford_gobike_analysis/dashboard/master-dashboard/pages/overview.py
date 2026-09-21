"""
pages/overview.py – Executive Overview Landing View
===================================================
Matches the exact SaaS visual aesthetic from Screenshot 1 & the reference platform:
  1. 6 Executive KPI Cards with deltas and sparklines
  2. Daily Ridership & Prior Period Benchmark Area Line Chart (Col 8)
  3. Computed System Insights Panel with real-time indicators (Col 4)
  4. Quick Launch Cards (Station Flow & Time Demographics)
  5. Collapsible Data Lineage & Schema Definition accordion
"""

from __future__ import annotations

from dash import html, dcc

from config import ROUTE_STATIONS, ROUTE_TIME_USER, ROUTE_USER_TRIPS
from components.kpi_banner import render_kpi_banner
from components.key_insights import render_key_insights
from components.overview_charts import create_overview_daily_trend_chart
from data_loader import (
    load_master_kpi_summary,
    load_overview_daily_trend,
)


def _render_architecture_accordion() -> html.Div:
    """
    Renders the Data Infrastructure & Lineage block collapsed inside
    a clean HTML5 <details> accordion matching the reference footer.
    """
    return html.Details(
        className="group bg-white rounded-xl border border-slate-200/90 shadow-2xs mb-6 overflow-hidden transition-all",
        children=[
            html.Summary(
                className="flex items-center justify-between p-4 cursor-pointer select-none hover:bg-slate-50 transition-colors list-none text-xs font-semibold text-slate-600",
                children=[
                    html.Div(
                        className="flex items-center gap-2.5",
                        children=[
                            html.I(className="fas fa-layer-group text-teal-600 text-sm"),
                            html.Span("About this platform, Data Lineage & Schema Definition", className="font-bold text-slate-800"),
                        ],
                    ),
                    html.Div(
                        className="flex items-center gap-3",
                        children=[
                            html.Span(
                                [
                                    html.Span(className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block mr-1.5 animate-pulse"),
                                    "Gold Layer · 174,724 Trips",
                                ],
                                className="hidden sm:inline-flex items-center text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200/60 px-2.5 py-0.5 rounded-full",
                            ),
                            html.I(className="fas fa-chevron-down text-[11px] text-slate-400 group-open:rotate-180 transition-transform duration-200"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="p-4 pt-2 border-t border-slate-100 bg-slate-50/50 text-xs text-slate-600",
                children=[
                    html.Div(
                        className="grid grid-cols-1 md:grid-cols-3 gap-3 text-[11px]",
                        children=[
                            html.Div(
                                className="p-3.5 rounded-lg bg-white border border-slate-200/80 shadow-2xs",
                                children=[
                                    html.Div(
                                        [html.I(className="fas fa-cloud text-indigo-500 mr-1.5"), "1. Cloud Data Warehouse"],
                                        className="font-bold text-slate-800 mb-1",
                                    ),
                                    html.P(
                                        "Supabase PostgreSQL serving curated gold.trip_analytics view with 174,724 completed rides.",
                                        className="text-slate-500 leading-relaxed",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="p-3.5 rounded-lg bg-white border border-slate-200/80 shadow-2xs",
                                children=[
                                    html.Div(
                                        [html.I(className="fas fa-cubes text-emerald-500 mr-1.5"), "2. Modular Pipeline Architecture"],
                                        className="font-bold text-slate-800 mb-1",
                                    ),
                                    html.P(
                                        "Decoupled analytics modules operating with isolated namespaces and synchronized global filters.",
                                        className="text-slate-500 leading-relaxed",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="p-3.5 rounded-lg bg-white border border-slate-200/80 shadow-2xs",
                                children=[
                                    html.Div(
                                        [html.I(className="fas fa-sitemap text-teal-500 mr-1.5"), "3. Unified Executive Suite"],
                                        className="font-bold text-slate-800 mb-1",
                                    ),
                                    html.P(
                                        "Real-time synthesis across San Francisco, East Bay, and San Jose transit clusters.",
                                        className="text-slate-500 leading-relaxed",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def render_overview_page() -> html.Div:
    """Renders the comprehensive Executive Overview landing dashboard matching Screenshot 1."""
    # 1. Ingest cached metrics and daily trajectory
    kpis = load_master_kpi_summary()
    daily_df = load_overview_daily_trend()

    # 2. Build Daily Ridership & Benchmark Chart
    fig_trend = create_overview_daily_trend_chart(daily_df)

    return html.Div(
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6",
        children=[
            # ── 1. 6 Executive KPI Cards Banner ───────────────────────────
            html.Div(
                id="overview-kpi-banner-container",
                children=render_kpi_banner(kpis),
            ),

            # ── 2. Visual Analytics Section (Daily Trend + Insights) ──────
            html.Section(
                className="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-6",
                children=[
                    # Daily Ridership & Prior Period Benchmark (Col 8)
                    html.Div(
                        className="lg:col-span-8 analytics-card p-5 flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-2",
                                children=[
                                    html.Div(
                                        children=[
                                            html.H3(
                                                "Daily Ridership & Prior Period Benchmark",
                                                className="text-sm font-bold text-slate-900",
                                            ),
                                            html.P(
                                                "Comparing current daily trajectory against previous corresponding window",
                                                className="text-xs text-slate-400 mt-0.5",
                                            ),
                                        ],
                                    ),
                                    html.Button(
                                        html.I(className="fas fa-download text-xs"),
                                        className="text-slate-400 hover:text-slate-700 p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors cursor-pointer",
                                        title="Download chart PNG",
                                        n_clicks=0,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="w-full",
                                children=[
                                    dcc.Graph(
                                        id="overview-trend-graph",
                                        figure=fig_trend,
                                        config={"displayModeBar": False},
                                        style={"height": "288px"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Computed System Insights Panel (Col 4)
                    html.Div(
                        id="overview-insights-container",
                        className="lg:col-span-4",
                        children=render_key_insights(kpis),
                    ),
                ],
            ),

            # ── 3. Quick Launch Navigation Cards (Side-by-Side) ───────────
            html.Section(
                className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6",
                children=[
                    # Station & Network Flow Intelligence
                    dcc.Link(
                        href=ROUTE_STATIONS,
                        className="analytics-card p-4 rounded-xl border border-slate-200/90 bg-white hover:border-slate-300 hover:shadow-xs transition-all flex items-center justify-between group cursor-pointer no-underline",
                        children=[
                            html.Div(
                                className="flex items-center gap-3.5",
                                children=[
                                    html.Div(
                                        className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 shrink-0",
                                        children=[html.I(className="fas fa-map-marked-alt text-base")],
                                    ),
                                    html.Div(
                                        children=[
                                            html.H4(
                                                "Station & Network Flow",
                                                className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors",
                                            ),
                                            html.P(
                                                "Interactive network maps, imbalance & dispatch routes.",
                                                className="text-xs text-slate-500 mt-0.5",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.I(className="fas fa-arrow-right text-xs text-slate-400 group-hover:text-slate-700 group-hover:translate-x-1 transition-all shrink-0 ml-2"),
                        ],
                    ),

                    # Temporal Demand & Rider Demographics
                    dcc.Link(
                        href=ROUTE_TIME_USER,
                        className="analytics-card p-4 rounded-xl border border-slate-200/90 bg-white hover:border-slate-300 hover:shadow-xs transition-all flex items-center justify-between group cursor-pointer no-underline",
                        children=[
                            html.Div(
                                className="flex items-center gap-3.5",
                                children=[
                                    html.Div(
                                        className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-100 flex items-center justify-center text-purple-600 shrink-0",
                                        children=[html.I(className="far fa-clock text-base")],
                                    ),
                                    html.Div(
                                        children=[
                                            html.H4(
                                                "Time & Demographics",
                                                className="text-sm font-bold text-slate-900 group-hover:text-purple-600 transition-colors",
                                            ),
                                            html.P(
                                                "Duration histograms, age cohorts & subscriber ratios.",
                                                className="text-xs text-slate-500 mt-0.5",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.I(className="fas fa-arrow-right text-xs text-slate-400 group-hover:text-slate-700 group-hover:translate-x-1 transition-all shrink-0 ml-2"),
                        ],
                    ),

                    # Rider & Trip Dynamics (Member 3)
                    dcc.Link(
                        href=ROUTE_USER_TRIPS,
                        className="analytics-card p-4 rounded-xl border border-slate-200/90 bg-white hover:border-slate-300 hover:shadow-xs transition-all flex items-center justify-between group cursor-pointer no-underline",
                        children=[
                            html.Div(
                                className="flex items-center gap-3.5",
                                children=[
                                    html.Div(
                                        className="w-10 h-10 rounded-xl bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-600 shrink-0",
                                        children=[html.I(className="fas fa-users-cog text-base")],
                                    ),
                                    html.Div(
                                        children=[
                                            html.H4(
                                                "Rider & Trip Dynamics",
                                                className="text-sm font-bold text-slate-900 group-hover:text-teal-600 transition-colors",
                                            ),
                                            html.P(
                                                "Gender behaviors, duration profiles & trip velocity.",
                                                className="text-xs text-slate-500 mt-0.5",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.I(className="fas fa-arrow-right text-xs text-slate-400 group-hover:text-slate-700 group-hover:translate-x-1 transition-all shrink-0 ml-2"),
                        ],
                    ),
                ],
            ),

            # ── 4. Collapsible Platform Lineage & Architecture ────────────
            _render_architecture_accordion(),
        ],
    )
