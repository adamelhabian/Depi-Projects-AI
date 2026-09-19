"""
layout.py – Clean Dashboard Layout for Member 4: Time & User Analysis
====================================================================
Tailwind CSS-driven layout containing:
  - Header with title and live cloud status badge
  - 4 KPI Headline Metric Cards
  - Responsive Filter Controls Bar
  - Exactly 5 Core Visualizations (2 Temporal + 3 Demographic/Behavioral)
  - Footer
"""

from __future__ import annotations

from dash import html
from config import (
    # KPIs
    ID_KPI_TOTAL_TRIPS,
    ID_KPI_SUBSCRIBER_PCT,
    ID_KPI_PEAK_HOUR,
    ID_KPI_AVG_DURATION,
    # Charts
    ID_TRIPS_BY_HOUR,
    ID_TRIPS_BY_DAY,
    ID_USER_TYPE_DISTRIBUTION,
    ID_USER_TYPE_HOUR,
    ID_AGE_GROUP_DISTRIBUTION,
    # Chart heights
    CHART_HEIGHT_LINE,
    CHART_HEIGHT_BAR,
)
from components.chart_card import chart_card
from components.filter_panel import filter_panel


def _kpi_card(title: str, value_id: str, default_value: str, subtitle: str, color_border: str) -> html.Div:
    """Render a single high-impact KPI summary tile."""
    return html.Div(
        className=f"bg-white rounded-2xl border border-slate-200/80 shadow-sm p-4 sm:p-5 flex flex-col justify-between {color_border}",
        children=[
            html.Div(
                className="flex items-center justify-between mb-2",
                children=[
                    html.Span(
                        title,
                        className="text-xs font-bold uppercase tracking-wider text-slate-500",
                    ),
                ],
            ),
            html.Div(
                id=value_id,
                className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight",
                children=default_value,
            ),
            html.P(
                subtitle,
                className="text-xs text-slate-400 mt-2",
            ),
        ],
    )


def create_layout() -> html.Div:
    """Build the complete, self-contained Time & User Analysis dashboard layout."""
    return html.Div(
        className="w-full flex flex-col gap-6",
        children=[
            # ── 1. Dashboard Header ─────────────────────────────────────────
            html.Header(
                className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4",
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                className="flex items-center gap-2 mb-1",
                                children=[
                                    html.Span(
                                        "Member 4 Analysis",
                                        className="text-[11px] font-bold tracking-wide uppercase px-2.5 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200",
                                    ),
                                    html.Span(
                                        "Behavioral & Temporal",
                                        className="text-[11px] font-semibold tracking-wide text-slate-400",
                                    ),
                                ],
                            ),
                            html.H1(
                                "Time & User Behavior Analytics",
                                className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight",
                            ),
                            html.P(
                                "Diurnal commuting rhythms, weekly usage intensity, and rider demographic segmentation.",
                                className="text-sm text-slate-500 mt-1",
                            ),
                        ],
                    ),
                    html.Div(
                        className="flex sm:flex-col items-center sm:items-end justify-between gap-1",
                        children=[
                            html.Div(
                                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs font-medium text-slate-700",
                                children=[
                                    html.Span(className="w-2 h-2 rounded-full bg-teal-500"),
                                    html.Span("Supabase Cloud Pipeline"),
                                ],
                            ),
                            html.Span(
                                "Table: gold.trip_analytics",
                                className="text-xs text-slate-400 font-mono hidden sm:inline",
                            ),
                        ],
                    ),
                ],
            ),

            # ── 2. Headline KPI Summary Cards ───────────────────────────────
            html.Section(
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
                children=[
                    _kpi_card(
                        "Total Trips",
                        ID_KPI_TOTAL_TRIPS,
                        "—",
                        "Total trip records matching current filter",
                        "border-l-4 border-l-teal-500",
                    ),
                    _kpi_card(
                        "Subscriber Ratio",
                        ID_KPI_SUBSCRIBER_PCT,
                        "—",
                        "Share of rides by annual pass holders",
                        "border-l-4 border-l-emerald-500",
                    ),
                    _kpi_card(
                        "Peak Commute Window",
                        ID_KPI_PEAK_HOUR,
                        "—",
                        "Hour with highest network traffic volume",
                        "border-l-4 border-l-purple-500",
                    ),
                    _kpi_card(
                        "Average Ride Duration",
                        ID_KPI_AVG_DURATION,
                        "—",
                        "Mean elapsed journey length in minutes",
                        "border-l-4 border-l-amber-500",
                    ),
                ],
            ),

            # ── 3. Filters & Slicers Bar ────────────────────────────────────
            filter_panel(),

            # ── 4. Core Visualizations Grid (5 Charts) ──────────────────────
            # Section A: Temporal Rhythms (2 Charts)
            html.Section(
                className="grid grid-cols-1 lg:grid-cols-12 gap-6",
                children=[
                    # Chart 1: Hourly Demand Profile (6 cols)
                    html.Div(
                        className="lg:col-span-6",
                        children=[
                            chart_card(
                                graph_id=ID_TRIPS_BY_HOUR,
                                title="Hourly Trip Demand Profile",
                                subtitle="Diurnal volume distribution highlighting morning (8–9 AM) and evening (5–6 PM) commuter peaks",
                                badge_text="Hourly Rhythm",
                                badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-100",
                                height=CHART_HEIGHT_LINE,
                            ),
                        ],
                    ),
                    # Chart 2: Day-of-Week Riding Volume (6 cols)
                    html.Div(
                        className="lg:col-span-6",
                        children=[
                            chart_card(
                                graph_id=ID_TRIPS_BY_DAY,
                                title="Day-of-Week Riding Volume",
                                subtitle="Volume comparison across the week highlighting weekday commuter demand vs weekend drop",
                                badge_text="Weekly Volume",
                                badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-100",
                                height=CHART_HEIGHT_BAR,
                            ),
                        ],
                    ),
                ],
            ),

            # Section B: User Dynamics & Demographics (3 Charts)
            html.Section(
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-6",
                children=[
                    # Chart 3: Subscriber vs Customer Split (4 cols)
                    html.Div(
                        className="lg:col-span-4",
                        children=[
                            chart_card(
                                graph_id=ID_USER_TYPE_DISTRIBUTION,
                                title="Rider Membership Split",
                                subtitle="Annual subscribers vs. casual pass riders",
                                badge_text="Membership",
                                badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700",
                                height=CHART_HEIGHT_BAR,
                            ),
                        ],
                    ),
                    # Chart 4: Hourly Pattern by User Type (4 cols)
                    html.Div(
                        className="lg:col-span-4",
                        children=[
                            chart_card(
                                graph_id=ID_USER_TYPE_HOUR,
                                title="Hourly Pattern by User Type",
                                subtitle="Subscribers drive commute spikes while casual customers ride midday",
                                badge_text="Behavioral",
                                badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-100",
                                height=CHART_HEIGHT_BAR,
                            ),
                        ],
                    ),
                    # Chart 5: Age Group Distribution (4 cols)
                    html.Div(
                        className="lg:col-span-4 md:col-span-2",
                        children=[
                            chart_card(
                                graph_id=ID_AGE_GROUP_DISTRIBUTION,
                                title="Rider Age Cohort Distribution",
                                subtitle="Trip volume distributed across demographic age cohorts",
                                badge_text="Demographics",
                                badge_class="text-xs font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-100",
                                height=CHART_HEIGHT_BAR,
                            ),
                        ],
                    ),
                ],
            ),

            # ── 5. Clean Footer ─────────────────────────────────────────────
            html.Footer(
                className="mt-6 py-6 border-t border-slate-200 text-center text-xs text-slate-400",
                children=[
                    html.P(
                        "Ford GoBike Analytics Project · Member 4: Time & User Analysis · Exclusively Powered by Supabase Cloud PostgreSQL",
                    ),
                ],
            ),
        ],
    )