"""
components/key_insights.py – Computed System Insights Panel
============================================================
Matches the exact SaaS visual card from the reference HTML and Screenshot 1:
  - Real-time pulse indicator & badge
  - 4 algorithmically synthesized operational insights
  - Contextual recommendation footer pointing to Station Flow
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from dash import html
import pandas as pd

from utils.metrics_calculator import (
    DEFAULT_KPIS,
    get_insight_commute_crest,
    get_insight_fleet_redistribution,
    get_insight_subscription_dominance,
    get_insight_leisure_ratio,
)


def _insight_item(
    icon_class: str,
    icon_color: str,
    title: str,
    text: str,
) -> html.Div:
    """Individual synthesized insight item inside the panel."""
    return html.Div(
        className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 hover:bg-slate-100/70 transition-colors",
        children=[
            html.Div(
                className="flex items-center gap-2 mb-1",
                children=[
                    html.I(className=f"{icon_class} {icon_color} text-xs shrink-0"),
                    html.Span(title, className="text-xs font-bold text-slate-900"),
                ],
            ),
            html.P(text, className="text-[11px] text-slate-500 leading-relaxed"),
        ],
    )


def render_key_insights(
    kpis: Optional[Dict[str, Any]] = None,
    hourly_df: Optional[pd.DataFrame] = None,
) -> html.Div:
    """
    Renders the Computed System Insights panel matching the reference UI.
    """
    if not kpis:
        kpis = DEFAULT_KPIS.copy()

    sub_pct = kpis.get("subscriber_pct", DEFAULT_KPIS["subscriber_pct"])
    avg_dur = kpis.get("avg_duration", DEFAULT_KPIS["avg_duration"])
    total_trips = kpis.get("total_trips", DEFAULT_KPIS["total_trips"])
    rebalance_count = kpis.get("rebalance_alerts", DEFAULT_KPIS["rebalance_alerts"])
    busiest_day = kpis.get("busiest_day", DEFAULT_KPIS["busiest_day"])
    ratio_str = kpis.get("duration_ratio_str", DEFAULT_KPIS["duration_ratio_str"])
    casual_dur = kpis.get("casual_duration_str", DEFAULT_KPIS["casual_duration_str"])
    sub_dur = kpis.get("sub_duration_str", DEFAULT_KPIS["sub_duration_str"])

    return html.Div(
        className="analytics-card p-5 flex flex-col justify-between h-full bg-white rounded-xl border border-slate-200/90 shadow-2xs",
        children=[
            html.Div(
                children=[
                    # Panel Header
                    html.Div(
                        className="flex items-center justify-between mb-2",
                        children=[
                            html.Div(
                                className="flex items-center gap-2",
                                children=[
                                    html.Span(className="w-2 h-2 rounded-full bg-teal-500 animate-pulse"),
                                    html.H3("Computed System Insights", className="text-sm font-bold text-slate-900"),
                                ],
                            ),
                            html.Span(
                                "REAL-TIME",
                                className="text-[10px] font-bold text-teal-600 bg-teal-50 border border-teal-100 px-2 py-0.5 rounded-full uppercase tracking-wider",
                            ),
                        ],
                    ),
                    html.P(
                        "Synthesized algorithmically from current slice of trip records.",
                        className="text-xs text-slate-400 mb-4",
                    ),

                    # Insights List
                    html.Div(
                        className="flex flex-col gap-2.5",
                        children=[
                            _insight_item(
                                icon_class="far fa-calendar-check",
                                icon_color="text-teal-600",
                                title="Weekly Commute Crest",
                                text=get_insight_commute_crest(busiest_day),
                            ),
                            _insight_item(
                                icon_class="fas fa-truck-fast",
                                icon_color="text-blue-600",
                                title="Fleet Redistribution Demand",
                                text=get_insight_fleet_redistribution(rebalance_count),
                            ),
                            _insight_item(
                                icon_class="fas fa-user-check",
                                icon_color="text-emerald-600",
                                title="Subscription Dominance",
                                text=get_insight_subscription_dominance(sub_pct, avg_dur),
                            ),
                            _insight_item(
                                icon_class="fas fa-compass",
                                icon_color="text-purple-600",
                                title="Rider Cohort Dynamic",
                                text=get_insight_leisure_ratio(ratio_str, casual_dur, sub_dur),
                            ),
                        ],
                    ),
                ],
            ),

            # Panel Recommendation Footer
            html.Div(
                className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-500 flex items-center gap-2",
                children=[
                    html.I(className="fas fa-compass text-teal-500 text-xs shrink-0"),
                    html.Span("Recommended next action: Review fleet dispatch pairings on the Station Flow page."),
                ],
            ),
        ],
    )
