"""
components/kpi_banner.py – Executive KPI Banner
================================================
Renders high-level fleet-wide KPI cards summarizing system performance,
trip volume, station count, and member utilization.
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from dash import html


def _kpi_card(
    title: str,
    value: str,
    subtitle: str,
    icon: str,
    accent_class: str,
    badge: Optional[str] = None,
) -> html.Div:
    """Individual KPI metric card."""
    return html.Div(
        className=f"overview-kpi-card bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs flex flex-col justify-between {accent_class}",
        children=[
            html.Div(
                className="flex items-center justify-between mb-3",
                children=[
                    html.Span(
                        title,
                        className="text-xs font-bold uppercase tracking-wider text-slate-500",
                    ),
                    html.Div(
                        className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600",
                        children=[
                            html.I(className=icon),
                        ],
                    ),
                ],
            ),
            html.Div(
                children=[
                    html.Div(
                        value,
                        className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight",
                    ),
                    html.P(
                        subtitle,
                        className="text-xs text-slate-500 mt-1.5 flex items-center gap-1.5",
                    ),
                ],
            ),
        ],
    )


def render_kpi_banner(kpis: Optional[Dict[str, Any]] = None) -> html.Section:
    """
    Renders the 4-card responsive KPI summary banner.
    """
    if not kpis:
        kpis = {
            "total_trips": "174,724",
            "unique_stations": "329",
            "subscriber_pct": "90.5%",
            "avg_duration": "11.7 min",
        }

    return html.Section(
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6",
        children=[
            _kpi_card(
                "Total Fleet Trips",
                kpis.get("total_trips", "174,724"),
                "Verified completed journeys in gold dataset",
                "fas fa-route",
                "border-l-4 border-l-indigo-500",
            ),
            _kpi_card(
                "Active Network Stations",
                kpis.get("unique_stations", "329"),
                "Connected docking hubs across Bay Area",
                "fas fa-map-pin",
                "border-l-4 border-l-emerald-500",
            ),
            _kpi_card(
                "Subscriber Adoption",
                kpis.get("subscriber_pct", "90.5%"),
                "Dominant annual commuter membership base",
                "fas fa-users",
                "border-l-4 border-l-teal-500",
            ),
            _kpi_card(
                "System Avg Duration",
                kpis.get("avg_duration", "11.7 min"),
                "Average trip length under 30-min threshold",
                "fas fa-stopwatch",
                "border-l-4 border-l-purple-500",
            ),
        ],
    )
