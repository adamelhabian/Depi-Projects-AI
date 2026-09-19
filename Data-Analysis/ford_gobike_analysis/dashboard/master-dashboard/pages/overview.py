"""
pages/overview.py – Executive Overview Landing View
===================================================
Consolidated executive overview displaying high-level system metrics,
cross-cutting operational insights, and direct entry points to deep-dive modules.
"""

from __future__ import annotations

from dash import html, dcc
import plotly.graph_objects as go

from config import ROUTE_STATIONS, ROUTE_TIME_USER
from components.kpi_banner import render_kpi_banner
from data_loader import load_master_kpi_summary


def _create_quick_launch_card(
    title: str,
    module_badge: str,
    module_badge_color: str,
    description: str,
    highlights: list[tuple[str, str]],
    route: str,
    btn_text: str,
    gradient_from: str,
    accent_color: str,
    icon: str,
) -> html.Div:
    """Creates a card linking directly to a deep-dive module."""
    highlight_badges = [
        html.Div(
            className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 last:border-0",
            children=[
                html.Span(label, className="text-slate-500"),
                html.Span(val, className="font-bold text-slate-800"),
            ],
        )
        for label, val in highlights
    ]

    return html.Div(
        className="quick-launch-card bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm flex flex-col justify-between hover:shadow-md transition-all",
        children=[
            html.Div(
                children=[
                    # Card Header
                    html.Div(
                        className="flex items-start justify-between mb-4",
                        children=[
                            html.Div(
                                className="flex items-center gap-3",
                                children=[
                                    html.Div(
                                        className=f"w-12 h-12 rounded-xl {gradient_from} flex items-center justify-center text-white shadow-md",
                                        children=[
                                            html.I(className=f"{icon} text-xl"),
                                        ],
                                    ),
                                    html.Div(
                                        children=[
                                            html.H3(
                                                title,
                                                className="text-lg font-bold text-slate-900 leading-tight",
                                            ),
                                            html.Span(
                                                module_badge,
                                                className=f"inline-block mt-0.5 text-[10px] font-bold px-2 py-0.5 rounded-full {module_badge_color}",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Card Description
                    html.P(
                        description,
                        className="text-sm text-slate-600 leading-relaxed mb-5",
                    ),

                    # Key Module Highlights
                    html.Div(
                        className="bg-slate-50 rounded-xl p-3.5 mb-6 border border-slate-100",
                        children=[
                            html.Div(
                                "Module Highlights & Capabilities",
                                className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2",
                            ),
                            html.Div(children=highlight_badges),
                        ],
                    ),
                ],
            ),

            # Card CTA Button
            dcc.Link(
                href=route,
                className=f"w-full inline-flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-white font-semibold text-sm shadow-sm transition-all {accent_color}",
                children=[
                    html.Span(btn_text),
                    html.I(className="fas fa-arrow-right text-xs"),
                ],
            ),
        ],
    )


def render_overview_page() -> html.Div:
    """Renders the executive overview landing page."""
    kpis = load_master_kpi_summary()

    return html.Div(
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
        children=[
            # 1. Headline Title Banner
            html.Div(
                className="mb-8",
                children=[
                    html.Div(
                        className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200/60 text-xs font-semibold text-indigo-700 mb-2",
                        children=[
                            html.I(className="fas fa-bolt text-[11px] text-indigo-500"),
                            html.Span("Unified Executive Analytics Suite"),
                        ],
                    ),
                    html.H1(
                        "Executive Fleet & Network Intelligence",
                        className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight",
                    ),
                    html.P(
                        "Holistic operational view synthesizing station network capacity, corridor movement, and commuter behavioral segmentation across the greater Bay Area.",
                        className="text-sm sm:text-base text-slate-500 mt-1 max-w-4xl",
                    ),
                ],
            ),

            # 2. Executive KPI Cards Banner
            render_kpi_banner(kpis),

            # 3. Deep-Dive Module Launch Cards
            html.Div(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8",
                children=[
                    _create_quick_launch_card(
                        title="Station & Network Flow Analysis",
                        module_badge="Module 5 · Geospatial Core",
                        module_badge_color="bg-emerald-100 text-emerald-800",
                        description="Geospatial distribution across 329 stations in San Francisco, East Bay, and San Jose. Inspect corridor flow imbalances, round-trip leisure routes, and docking capacity requirements.",
                        highlights=[
                            ("Geospatial Scope", "329 Stations across 3 Sub-Regions"),
                            ("Network Dynamics", "Top 10–30 Corridors & Flow Imbalance"),
                            ("Data Layer", "Direct Supabase Live Ingestion"),
                        ],
                        route=ROUTE_STATIONS,
                        btn_text="Launch Station & Network Dashboard",
                        gradient_from="bg-gradient-to-tr from-emerald-500 to-teal-600",
                        accent_color="bg-emerald-600 hover:bg-emerald-700 shadow-emerald-500/20",
                        icon="fas fa-map-marked-alt",
                    ),
                    _create_quick_launch_card(
                        title="Time & User Demographics Analysis",
                        module_badge="Module 4 · Behavioral Core",
                        module_badge_color="bg-teal-100 text-teal-800",
                        description="Deep-dive into diurnal commuting rhythms, 8 AM and 5 PM rush hour traffic volumes, the 90.5% subscriber ecosystem, and rider age cohort segmentation.",
                        highlights=[
                            ("Commuter Peak Demand", "8:00 AM & 5:00 PM Weekday Spikes"),
                            ("User Composition", "90.5% Subscribers vs 9.5% Customers"),
                            ("Core Age Cohort", "26–35 Years (47.6% of all rides)"),
                        ],
                        route=ROUTE_TIME_USER,
                        btn_text="Launch Time & User Dashboard",
                        gradient_from="bg-gradient-to-tr from-teal-500 to-indigo-600",
                        accent_color="bg-teal-600 hover:bg-teal-700 shadow-teal-500/20",
                        icon="fas fa-user-clock",
                    ),
                ],
            ),

            # 4. System Architecture & Infrastructure Footprint
            html.Section(
                className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs",
                children=[
                    html.Div(
                        className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 gap-2",
                        children=[
                            html.Div(
                                children=[
                                    html.H4(
                                        "Platform Data Infrastructure & Lineage",
                                        className="text-base font-bold text-slate-800",
                                    ),
                                    html.P(
                                        "Enterprise architecture connecting cloud storage directly to real-time analytics.",
                                        className="text-xs text-slate-500",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="inline-flex items-center gap-2 text-xs text-slate-600 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200/60 font-mono",
                                children=[
                                    html.Span(className="w-2 h-2 rounded-full bg-emerald-500"),
                                    html.Span("Gold Layer · 174,724 Validated Records"),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs",
                        children=[
                            html.Div(
                                className="p-4 rounded-xl bg-slate-50 border border-slate-100",
                                children=[
                                    html.Div("1. Storage & Warehouse", className="font-bold text-slate-800 mb-1"),
                                    html.P("Supabase PostgreSQL cloud instance hosting curated Gold analytics tables with 0 CSV dependencies.", className="text-slate-500 leading-relaxed"),
                                ],
                            ),
                            html.Div(
                                className="p-4 rounded-xl bg-slate-50 border border-slate-100",
                                children=[
                                    html.Div("2. Modular Component Architecture", className="font-bold text-slate-800 mb-1"),
                                    html.P("Decoupled member modules running independently with zero component ID collisions (`m5-*` and `tu-*`).", className="text-slate-500 leading-relaxed"),
                                ],
                            ),
                            html.Div(
                                className="p-4 rounded-xl bg-slate-50 border border-slate-100",
                                children=[
                                    html.Div("3. Unified Master Gateway", className="font-bold text-slate-800 mb-1"),
                                    html.P("Centralized routing, executive KPI synthesis, and responsive sidebar navigation linking all insights.", className="text-slate-500 leading-relaxed"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
