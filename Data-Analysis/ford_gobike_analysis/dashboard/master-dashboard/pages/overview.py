"""
pages/overview.py – Executive Overview Landing View
===================================================
Consolidated executive analytics platform synthesizing:
  1. Executive Headline & Live Pipeline Status
  2. 4 Executive KPI Cards with embedded Plotly sparklines & deltas
  3. Strategic Key Insights Panel (auto-generated from data)
  4. Visual Analytics Grid: 24-Hour Demand Trend (Dual-Axis) & Regional Mini-Map
  5. Direct Deep-Dive Module Launch Cards (M-5 Stations & M-4 Time/User)
  6. Collapsed Architecture Accordion (Data Infrastructure & Lineage)
"""

from __future__ import annotations

from dash import html, dcc

from config import ROUTE_STATIONS, ROUTE_TIME_USER
from components.kpi_banner import render_kpi_banner
from components.key_insights import render_key_insights
from components.overview_charts import (
    create_overview_trend_chart,
    create_overview_minimap,
)
from data_loader import (
    load_master_kpi_summary,
    load_overview_hourly_trend,
    load_overview_station_points,
)


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
    """Creates an actionable card linking directly to a deep-dive module."""
    highlight_badges = [
        html.Div(
            className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 last:border-0",
            children=[
                html.Span(label, className="text-slate-500"),
                html.Span(val, className="font-bold text-slate-800 font-mono"),
            ],
        )
        for label, val in highlights
    ]

    return html.Div(
        className="quick-launch-card bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs flex flex-col justify-between hover:shadow-md hover:border-slate-300 transition-all",
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
                                        className=f"w-11 h-11 rounded-xl {gradient_from} flex items-center justify-center text-white shadow-md",
                                        children=[
                                            html.I(className=f"{icon} text-lg"),
                                        ],
                                    ),
                                    html.Div(
                                        children=[
                                            html.H3(
                                                title,
                                                className="text-base sm:text-lg font-bold text-slate-900 leading-tight",
                                            ),
                                            html.Span(
                                                module_badge,
                                                className=f"inline-block mt-1 text-[10px] font-extrabold tracking-wider uppercase px-2 py-0.5 rounded-full {module_badge_color}",
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
                        className="text-xs text-slate-600 leading-relaxed mb-4",
                    ),

                    # Key Module Highlights
                    html.Div(
                        className="bg-slate-50 rounded-xl p-3.5 mb-5 border border-slate-100",
                        children=[
                            html.Div(
                                "Module Scope & Core Focus",
                                className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2",
                            ),
                            html.Div(children=highlight_badges),
                        ],
                    ),
                ],
            ),

            # Card CTA Link Button
            dcc.Link(
                href=route,
                className=f"w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-white font-semibold text-xs shadow-sm transition-all {accent_color}",
                children=[
                    html.Span(btn_text),
                    html.I(className="fas fa-arrow-right text-[11px]"),
                ],
            ),
        ],
    )


def _render_architecture_accordion() -> html.Div:
    """
    Renders the Data Infrastructure & Pipeline block collapsed inside
    a modern HTML5 <details> accordion so it doesn't crowd executive metrics.
    """
    return html.Details(
        className="group bg-white rounded-2xl border border-slate-200/90 shadow-xs mb-8 overflow-hidden transition-all",
        children=[
            # Accordion Header / Toggle
            html.Summary(
                className="flex items-center justify-between p-4 sm:p-5 cursor-pointer select-none hover:bg-slate-50 transition-colors list-none",
                children=[
                    html.Div(
                        className="flex items-center gap-3",
                        children=[
                            html.Div(
                                className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 text-sm",
                                children=[html.I(className="fas fa-database")],
                            ),
                            html.Div(
                                children=[
                                    html.H4(
                                        "Platform Data Infrastructure & Lineage",
                                        className="text-sm font-bold text-slate-900 leading-snug",
                                    ),
                                    html.P(
                                        "Click to inspect cloud pipeline architecture and zero-CSV contract.",
                                        className="text-[11px] text-slate-400",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="flex items-center gap-3",
                        children=[
                            html.Span(
                                [
                                    html.Span(className="w-2 h-2 rounded-full bg-emerald-500 inline-block mr-1.5 animate-pulse"),
                                    "Gold Layer · 174,724 Records",
                                ],
                                className="hidden sm:inline-flex items-center text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200/60 px-3 py-1 rounded-full",
                            ),
                            html.I(className="fas fa-chevron-down text-xs text-slate-400 group-open:rotate-180 transition-transform duration-200"),
                        ],
                    ),
                ],
            ),

            # Accordion Collapsible Content
            html.Div(
                className="p-5 pt-2 border-t border-slate-100 bg-slate-50/50",
                children=[
                    html.Div(
                        className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs",
                        children=[
                            html.Div(
                                className="p-4 rounded-xl bg-white border border-slate-200/80 shadow-2xs",
                                children=[
                                    html.Div(
                                        [
                                            html.I(className="fas fa-cloud text-indigo-500 mr-1.5"),
                                            "1. Cloud Storage & Warehouse",
                                        ],
                                        className="font-bold text-slate-800 mb-1.5 text-xs",
                                    ),
                                    html.P(
                                        "Supabase PostgreSQL hosted database serving curated gold.trip_analytics view with 0 local CSV file dependencies.",
                                        className="text-slate-500 leading-relaxed text-[11px]",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="p-4 rounded-xl bg-white border border-slate-200/80 shadow-2xs",
                                children=[
                                    html.Div(
                                        [
                                            html.I(className="fas fa-cubes text-emerald-500 mr-1.5"),
                                            "2. Modular Component Architecture",
                                        ],
                                        className="font-bold text-slate-800 mb-1.5 text-xs",
                                    ),
                                    html.P(
                                        "Decoupled analytics modules operating with isolated namespaces (m5-* and tu-*) eliminating callback collisions.",
                                        className="text-slate-500 leading-relaxed text-[11px]",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="p-4 rounded-xl bg-white border border-slate-200/80 shadow-2xs",
                                children=[
                                    html.Div(
                                        [
                                            html.I(className="fas fa-sitemap text-teal-500 mr-1.5"),
                                            "3. Unified Master Gateway",
                                        ],
                                        className="font-bold text-slate-800 mb-1.5 text-xs",
                                    ),
                                    html.P(
                                        "Synchronized global filter bar, responsive fixed sidebar, and live KPI synthesis across all Bay Area clusters.",
                                        className="text-slate-500 leading-relaxed text-[11px]",
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
    """Renders the comprehensive Executive Overview landing dashboard."""
    # 1. Ingest cached metrics and trends from Supabase
    kpis = load_master_kpi_summary()
    hourly_df = load_overview_hourly_trend()
    stations_df = load_overview_station_points()

    # Extract hourly volumes for sparklines
    hourly_volumes = hourly_df["trip_count"].tolist() if not hourly_df.empty else None

    # 2. Build Charts
    fig_trend = create_overview_trend_chart(hourly_df)
    fig_map = create_overview_minimap(stations_df)

    return html.Div(
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
        children=[
            # ── 1. Headline Title Banner ──────────────────────────────────
            html.Div(
                className="mb-8",
                children=[
                    html.Div(
                        className="flex flex-wrap items-center gap-2 mb-2",
                        children=[
                            html.Div(
                                className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200/60 text-xs font-semibold text-indigo-700",
                                children=[
                                    html.I(className="fas fa-bolt text-[11px] text-indigo-500"),
                                    html.Span("Unified Executive Analytics Suite"),
                                ],
                            ),
                            html.Div(
                                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200/60 text-xs font-semibold text-emerald-700",
                                children=[
                                    html.Span(className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"),
                                    html.Span("Live Cloud Pipeline · Supabase Gold"),
                                ],
                            ),
                        ],
                    ),
                    html.H1(
                        "Executive Fleet & Network Intelligence",
                        className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight",
                    ),
                    html.P(
                        "Holistic operational synthesis integrating docking capacity, corridor flows, diurnal rush hour curves, and subscriber retention across the greater Bay Area.",
                        className="text-xs sm:text-sm text-slate-500 mt-1 max-w-4xl leading-relaxed",
                    ),
                ],
            ),

            # ── 2. Executive KPI Cards Banner (with Sparklines & Deltas) ──
            render_kpi_banner(kpis, hourly_volumes),

            # ── 3. Strategic Key Insights Panel (Auto-Generated) ──────────
            render_key_insights(kpis, hourly_df),

            # ── 4. Visual Analytics Section (Trend Chart + Mini-Map) ───────
            html.Section(
                className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8",
                children=[
                    # 24-Hour Diurnal Trend Chart (Col 7)
                    html.Div(
                        className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs flex flex-col justify-between",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-3",
                                children=[
                                    html.Div(
                                        children=[
                                            html.H3(
                                                "24-Hour Fleet Volume & Duration Trend",
                                                className="text-sm font-bold text-slate-900",
                                            ),
                                            html.P(
                                                "Diurnal commute rhythm: Volume surges vs average journey length.",
                                                className="text-xs text-slate-500",
                                            ),
                                        ],
                                    ),
                                    html.Span(
                                        "Dual-Axis",
                                        className="text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100",
                                    ),
                                ],
                            ),
                            dcc.Graph(
                                figure=fig_trend,
                                config={"displayModeBar": False},
                                style={"height": "320px"},
                            ),
                        ],
                    ),

                    # Bay Area Regional Network Mini-Map (Col 5)
                    html.Div(
                        className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs flex flex-col justify-between",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-3",
                                children=[
                                    html.Div(
                                        children=[
                                            html.H3(
                                                "Bay Area Regional Network Density",
                                                className="text-sm font-bold text-slate-900",
                                            ),
                                            html.P(
                                                "329 docking stations across SF, East Bay & San Jose.",
                                                className="text-xs text-slate-500",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="flex items-center gap-1 text-[10px] font-bold",
                                        children=[
                                            html.Span("● SF", className="text-emerald-600 mr-1"),
                                            html.Span("● East Bay", className="text-teal-600 mr-1"),
                                            html.Span("● SJ", className="text-indigo-600"),
                                        ],
                                    ),
                                ],
                            ),
                            dcc.Graph(
                                figure=fig_map,
                                config={"displayModeBar": False},
                                style={"height": "320px"},
                            ),
                        ],
                    ),
                ],
            ),

            # ── 5. Deep-Dive Module Launch Cards ──────────────────────────
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

            # ── 6. Collapsed Architecture Accordion (Data Infrastructure) ─
            _render_architecture_accordion(),
        ],
    )
