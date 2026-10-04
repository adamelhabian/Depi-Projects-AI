"""
components/kpi_banner.py – Executive KPI Banner (6 High-Contrast Cards)
========================================================================
Matches the exact SaaS visual aesthetic from the reference platform:
  1. Total Trips (Value, ▲ +4.8% delta, sparkline)
  2. Active Stations (Value, ● Operational status, sparkline)
  3. Subscriber Ratio (Value, ▲ +0.7% delta, sparkline)
  4. Avg Duration (Value, ▼ -0.3 min delta, sparkline)
  5. Peak Commute (17:00 in purple, Evening rush, PM Peak badge)
  6. Rebalance Alerts (13 in orange, Needs Van Dispatch, warning alert)
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
from dash import html, dcc
import plotly.graph_objects as go

from utils.metrics_calculator import DEFAULT_KPIS


def _create_sparkline(
    y_values: List[float],
    color: str = "#14B8A6",
    fill_rgba: str = "rgba(20, 184, 166, 0.12)",
) -> go.Figure:
    """Create a minimalist micro-sparkline figure without axes or margins."""
    fig = go.Figure(
        go.Scatter(
            y=y_values,
            mode="lines",
            line=dict(color=color, width=2, shape="spline"),
            fill="tozeroy",
            fillcolor=fill_rgba,
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=24,
        width=68,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_kpi_banner(
    kpis: Optional[Dict[str, Any]] = None,
    hourly_volumes: Optional[List[float]] = None,
) -> html.Section:
    """
    Renders the 6-card responsive executive KPI summary banner matching the reference UI.
    """
    if not kpis:
        kpis = DEFAULT_KPIS.copy()

    # Hourly distribution for sparkline curve
    if not hourly_volumes or len(hourly_volumes) < 8:
        hourly_volumes = [
            800, 500, 300, 200, 150, 500, 2400, 7800, 17300, 12400,
            7800, 6900, 7400, 7200, 6800, 8900, 14200, 21800, 16900, 10200,
            6400, 4800, 3100, 1800
        ]

    # Sparklines
    spark_trips = _create_sparkline([1400, 1500, 1450, 1620, 1580, 1720, 1690, 1780], color="#14B8A6")
    spark_stations = _create_sparkline([320, 322, 325, 326, 328, 329, 329, 329], color="#94A3B8", fill_rgba="rgba(148, 163, 184, 0.12)")
    spark_subs = _create_sparkline([88.5, 89.0, 89.4, 89.8, 90.1, 90.3, 90.5], color="#14B8A6")
    spark_dur = _create_sparkline([12.4, 12.1, 11.9, 11.8, 11.7, 11.6, 11.7], color="#14B8A6")

    return html.Section(
        className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5 sm:gap-3.5 mb-4 sm:mb-6",
        children=[
            # ── KPI 1: Total Trips ──────────────────────────────────────────
            html.Div(
                className="analytics-card p-2.5 sm:p-4 relative overflow-hidden flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow min-w-0",
                children=[
                    html.Div(
                        className="flex items-center justify-between mb-1 min-w-0",
                        children=[
                            html.Span("Total Trips", className="text-[11px] sm:text-xs font-medium text-slate-500 truncate"),
                            html.Span(
                                html.I(className="fas fa-info-circle text-[10px] sm:text-[11px] text-slate-400 hover:text-slate-600 cursor-pointer shrink-0"),
                                title="Point-to-point bike rides in selected timeframe.",
                            ),
                        ],
                    ),
                    html.Div(
                        kpis.get("total_trips", DEFAULT_KPIS["total_trips"]),
                        className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight my-0.5 sm:my-1 truncate",
                    ),
                    html.Div(
                        className="flex items-center justify-between mt-1.5 sm:mt-2 pt-1.5 sm:pt-2 border-t border-slate-100 min-w-0 overflow-hidden",
                        children=[
                            html.Span("n/a", className="text-[10px] sm:text-xs font-semibold text-slate-400 truncate", title="No prior comparison period available for full 28-day dataset"),
                            dcc.Graph(
                                figure=spark_trips,
                                config={"displayModeBar": False, "staticPlot": True},
                                style={"height": "22px", "width": "55px"},
                                className="shrink-0",
                            ),
                        ],
                    ),
                ],
            ),

            # ── KPI 2: Active Stations ──────────────────────────────────────
            html.Div(
                className="analytics-card p-2.5 sm:p-4 relative overflow-hidden flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow min-w-0",
                children=[
                    html.Div(
                        className="flex items-center justify-between mb-1 min-w-0",
                        children=[
                            html.Span("Active Stations", className="text-[11px] sm:text-xs font-medium text-slate-500 truncate"),
                            html.Span(
                                html.I(className="fas fa-info-circle text-[10px] sm:text-[11px] text-slate-400 hover:text-slate-600 cursor-pointer shrink-0"),
                                title="Total operational docking hubs with at least one departure or arrival.",
                            ),
                        ],
                    ),
                    html.Div(
                        kpis.get("unique_stations", DEFAULT_KPIS["unique_stations"]),
                        className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight my-0.5 sm:my-1 truncate",
                    ),
                    html.Div(
                        className="flex items-center justify-between mt-1.5 sm:mt-2 pt-1.5 sm:pt-2 border-t border-slate-100 min-w-0 overflow-hidden",
                        children=[
                            html.Span("Operational", className="text-[10px] sm:text-[11px] font-semibold text-slate-600 truncate"),
                            dcc.Graph(
                                figure=spark_stations,
                                config={"displayModeBar": False, "staticPlot": True},
                                style={"height": "22px", "width": "55px"},
                                className="shrink-0",
                            ),
                        ],
                    ),
                ],
            ),

            # ── KPI 3: Subscriber Share ─────────────────────────────────────
            html.Div(
                className="analytics-card p-2.5 sm:p-4 relative overflow-hidden flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow min-w-0",
                children=[
                    html.Div(
                        className="flex items-center justify-between mb-1 min-w-0",
                        children=[
                            html.Span("Subscriber Share", className="text-[11px] sm:text-xs font-medium text-slate-500 truncate"),
                            html.Span(
                                html.I(className="fas fa-info-circle text-[10px] sm:text-[11px] text-slate-400 hover:text-slate-600 cursor-pointer shrink-0"),
                                title="Proportion of total trips completed by annual members vs casual customers.",
                            ),
                        ],
                    ),
                    html.Div(
                        kpis.get("subscriber_pct", DEFAULT_KPIS["subscriber_pct"]),
                        className="text-xl sm:text-2xl font-black text-teal-600 tracking-tight my-0.5 sm:my-1 truncate",
                    ),
                    html.Div(
                        className="flex items-center justify-between mt-1.5 sm:mt-2 pt-1.5 sm:pt-2 border-t border-slate-100 min-w-0 overflow-hidden",
                        children=[
                            html.Span("Annual pass", className="text-[10px] sm:text-[11px] font-semibold text-teal-700 truncate"),
                            dcc.Graph(
                                figure=spark_subs,
                                config={"displayModeBar": False, "staticPlot": True},
                                style={"height": "22px", "width": "55px"},
                                className="shrink-0",
                            ),
                        ],
                    ),
                ],
            ),

            # ── KPI 4: Median Duration ──────────────────────────────────────
            html.Div(
                className="analytics-card p-2.5 sm:p-4 relative overflow-hidden flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow min-w-0",
                children=[
                    html.Div(
                        className="flex items-center justify-between mb-1 min-w-0",
                        children=[
                            html.Span("Median Duration", className="text-[11px] sm:text-xs font-medium text-slate-500 truncate"),
                            html.Span(
                                html.I(className="fas fa-info-circle text-[10px] sm:text-[11px] text-slate-400 hover:text-slate-600 cursor-pointer shrink-0"),
                                title="50th-percentile trip length across fleet.",
                            ),
                        ],
                    ),
                    html.Div(
                        kpis.get("median_duration", DEFAULT_KPIS["median_duration"]),
                        className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight my-0.5 sm:my-1 truncate",
                    ),
                    html.Div(
                        className="flex items-center justify-between mt-1.5 sm:mt-2 pt-1.5 sm:pt-2 border-t border-slate-100 min-w-0 overflow-hidden",
                        children=[
                            html.Span("Per trip avg", className="text-[10px] sm:text-[11px] font-semibold text-slate-600 truncate"),
                            dcc.Graph(
                                figure=spark_dur,
                                config={"displayModeBar": False, "staticPlot": True},
                                style={"height": "22px", "width": "55px"},
                                className="shrink-0",
                            ),
                        ],
                    ),
                ],
            ),

            # ── KPI 5: Peak Commute ─────────────────────────────────────────
            html.Div(
                className="analytics-card p-2.5 sm:p-4 relative overflow-hidden flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow min-w-0",
                children=[
                    html.Div(
                        className="flex items-center justify-between mb-1 min-w-0",
                        children=[
                            html.Span("Peak Commute", className="text-[11px] sm:text-xs font-medium text-slate-500 truncate"),
                            html.Span(
                                html.I(className="fas fa-info-circle text-[10px] sm:text-[11px] text-slate-400 hover:text-slate-600 cursor-pointer shrink-0"),
                                title="Hour with highest simultaneous dispatch volume.",
                            ),
                        ],
                    ),
                    html.Div(
                        kpis.get("peak_commute", DEFAULT_KPIS["peak_commute"]),
                        className="text-xl sm:text-2xl font-black text-purple-600 tracking-tight my-0.5 sm:my-1 truncate",
                    ),
                    html.Div(
                        className="flex items-center justify-between mt-1.5 sm:mt-2 pt-1.5 sm:pt-2 border-t border-slate-100 min-w-0 overflow-hidden",
                        children=[
                            html.Span("Evening rush", className="text-[10px] sm:text-xs font-medium text-slate-500 truncate"),
                            html.Span("PM Peak", className="text-[9px] sm:text-[10px] font-bold text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded border border-purple-100 shrink-0"),
                        ],
                    ),
                ],
            ),

            # ── KPI 6: Rebalance Alerts ─────────────────────────────────────
            html.Div(
                className="analytics-card p-2.5 sm:p-4 relative overflow-hidden flex flex-col justify-between bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow min-w-0",
                children=[
                    html.Div(
                        className="flex items-center justify-between mb-1 min-w-0",
                        children=[
                            html.Span("Rebalance Alerts", className="text-[11px] sm:text-xs font-medium text-slate-500 truncate"),
                            html.Span(
                                html.I(className="fas fa-info-circle text-[10px] sm:text-[11px] text-slate-400 hover:text-slate-600 cursor-pointer shrink-0"),
                                title=kpis.get("rebalance_tooltip", DEFAULT_KPIS["rebalance_tooltip"]),
                            ),
                        ],
                    ),
                    html.Div(
                        str(kpis.get("rebalance_alerts", DEFAULT_KPIS["rebalance_alerts"])),
                        className="text-xl sm:text-2xl font-black text-orange-500 tracking-tight my-0.5 sm:my-1 truncate",
                    ),
                    html.Div(
                        className="flex items-center justify-between mt-1.5 sm:mt-2 pt-1.5 sm:pt-2 border-t border-slate-100 min-w-0 overflow-hidden",
                        children=[
                            html.Span("Net deficit hubs", className="text-[10px] sm:text-xs font-medium text-slate-500 truncate"),
                            html.Span("Action req.", className="text-[9px] sm:text-[10px] font-bold text-orange-600 bg-orange-50 px-1.5 py-0.5 rounded border border-orange-100 shrink-0"),
                        ],
                    ),
                ],
            ),
        ],
    )
