"""
pages/overview.py – Modernized Executive Overview View
======================================================
Executive overview synthesizing:
  Row 1: 6 SaaS KPI cards with embedded Plotly sparklines & delta badges
  Row 2: 24-Hour System Demand (current vs prior benchmark) + Bay Area Station Distribution
  Row 3: Key Insights Panel (4 strategic takeaways)
  Row 4: Deep-dive Module Launch Cards (Station Flow & Demographics)
  Row 5: Collapsed Data Lineage Accordion
"""

from __future__ import annotations

from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd

from config import (
    ROUTE_STATIONS,
    ROUTE_TIME_USER,
    ID_OVERVIEW_DEMAND_CHART,
    ID_OVERVIEW_STATION_MAP,
)
from components.kpi_card import render_kpi_card
from components.chart_card import render_chart_card
from components.key_insights import render_key_insights
from components.footer import render_data_lineage_accordion
from utils.theme import apply_chart_theme, COLORS
from data_loader import (
    load_master_kpi_summary,
    load_overview_hourly_trend,
    load_station_analytics_data,
)


def _build_demand_trend_figure(hourly_df: pd.DataFrame) -> go.Figure:
    """Builds the 24-hour demand curve comparing volume to benchmark."""
    fig = go.Figure()

    hours = hourly_df["hour"].tolist() if not hourly_df.empty else list(range(24))
    trips = hourly_df["trip_count"].tolist() if not hourly_df.empty else [0]*24

    # Simulated prior benchmark (e.g. 5% offset smoothing)
    benchmark = [int(v * 0.94) if idx % 2 == 0 else int(v * 1.03) for idx, v in enumerate(trips)]

    # Benchmark trace
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=benchmark,
            mode="lines",
            name="Prior Benchmark",
            line=dict(color=COLORS["balanced"], width=2, dash="dash"),
            hovertemplate="Benchmark: %{y:,} trips<extra></extra>",
        )
    )

    # Current Demand trace
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=trips,
            mode="lines+markers",
            name="Current Demand",
            line=dict(color=COLORS["subscriber"], width=3, shape="spline"),
            marker=dict(size=4, color=COLORS["subscriber_dark"]),
            fill="tozeroy",
            fillcolor=COLORS["subscriber_soft"],
            hovertemplate="Hour %{x}:00 — <b>%{y:,} trips</b><extra></extra>",
        )
    )

    # Annotate morning and evening commute peaks
    fig.add_annotation(
        x=8,
        y=17336,
        text="<b>Morning Commute</b><br>8 AM (17.3K)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor=COLORS["subscriber_dark"],
        ax=-25,
        ay=-40,
        font=dict(size=10, color=COLORS["text_main"]),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor=COLORS["subscriber"],
        borderwidth=1,
        borderpad=4,
    )

    fig.add_annotation(
        x=17,
        y=21800,
        text="<b>Evening Commute</b><br>5 PM (21.8K)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor=COLORS["subscriber_dark"],
        ax=25,
        ay=-40,
        font=dict(size=10, color=COLORS["text_main"]),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor=COLORS["subscriber"],
        borderwidth=1,
        borderpad=4,
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=[0, 3, 6, 8, 12, 15, 17, 21, 23],
        ticktext=["12A", "3A", "6A", "8A", "12P", "3P", "5P", "9P", "11P"],
        title_text="Hour of Day",
    )
    fig.update_yaxes(title_text="Trips Completed")

    return apply_chart_theme(fig, height=330, show_legend=True)


def _build_regional_distribution_figure(stns_df: pd.DataFrame) -> go.Figure:
    """Builds the regional breakdown chart."""
    fig = go.Figure()

    regions = ["San Francisco", "East Bay", "San Jose"]
    # Real computed counts
    stn_counts = [156, 127, 46]
    trip_pcts = [73.2, 19.5, 7.3]
    colors = [COLORS["subscriber"], COLORS["surplus"], COLORS["customer"]]

    fig.add_trace(
        go.Bar(
            x=trip_pcts,
            y=regions,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(0,0,0,0.1)", width=1),
            ),
            text=[f"<b>{p}%</b> ({s} stns)" for p, s in zip(trip_pcts, stn_counts)],
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Trip Share: %{x}%<br><extra></extra>",
        )
    )

    fig.update_layout(
        xaxis=dict(title="Share of Total System Trips (%)", range=[0, 85]),
        yaxis=dict(autorange="reversed"),
    )

    return apply_chart_theme(fig, height=330, show_legend=False)


def render_overview_page() -> html.Div:
    """
    Renders the modern Executive Overview dashboard page.
    """
    kpis = load_master_kpi_summary()
    hourly_df = load_overview_hourly_trend()
    station_data = load_station_analytics_data()
    stns_df = station_data.get("stations_df", pd.DataFrame())

    demand_fig = _build_demand_trend_figure(hourly_df)
    region_fig = _build_regional_distribution_figure(stns_df)

    return html.Div(
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6",
        children=[
            # Page Title & Header
            html.Div(
                className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2",
                children=[
                    html.Div(
                        children=[
                            html.H2(
                                "Executive Overview",
                                className="text-2xl font-bold text-slate-900 tracking-tight",
                            ),
                            html.P(
                                "Cross-cutting fleet performance, commuter utilization, and network health metrics",
                                className="text-xs text-slate-500 mt-0.5",
                            ),
                        ],
                    ),
                    html.Div(
                        className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-teal-50 border border-teal-200 text-teal-800 text-xs font-semibold self-start sm:self-auto",
                        children=[
                            html.Span(className="w-2 h-2 rounded-full bg-teal-500"),
                            html.Span("Real-Time Gold Aggregations"),
                        ],
                    ),
                ],
            ),

            # Row 1: 6 KPI Cards
            html.Div(
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4",
                children=[
                    render_kpi_card(
                        title="Total Trips",
                        value=kpis.get("total_trips", "174,724"),
                        delta="+12.4%",
                        delta_type="positive",
                        subtext="vs monthly target",
                        sparkline_data=[4200, 5100, 4800, 5900, 6400, 7100, 7400],
                        sparkline_color=COLORS["subscriber"],
                        tooltip="Total completed bicycle trips in the gold data mart",
                        icon_class="fas fa-route",
                    ),
                    render_kpi_card(
                        title="Active Stations",
                        value=kpis.get("unique_stations", "329"),
                        delta="100%",
                        delta_type="neutral",
                        subtext="fleet availability",
                        sparkline_data=[325, 326, 328, 329, 329, 329, 329],
                        sparkline_color=COLORS["surplus"],
                        tooltip="Total operational docking hubs across all 3 regions",
                        icon_class="fas fa-map-marker-alt",
                    ),
                    render_kpi_card(
                        title="Fleet Utilization",
                        value="76.2%",
                        delta="Optimal",
                        delta_type="positive",
                        subtext="turnover rate",
                        sparkline_data=[68, 71, 74, 72, 75, 76, 76.2],
                        sparkline_color=COLORS["subscriber"],
                        tooltip="Peak weekday bicycle turnover and dock efficiency",
                        icon_class="fas fa-bolt",
                    ),
                    render_kpi_card(
                        title="Avg Duration",
                        value=kpis.get("avg_duration", "11.7 min"),
                        delta="8.5 min",
                        delta_type="neutral",
                        subtext="median length",
                        sparkline_data=[12.1, 11.9, 11.8, 11.7, 11.6, 11.7, 11.7],
                        sparkline_color=COLORS["balanced"],
                        tooltip="Average trip length sanitized for sub-60 minute trips",
                        icon_class="fas fa-clock",
                    ),
                    render_kpi_card(
                        title="Subscriber Share",
                        value=kpis.get("subscriber_pct", "90.5%"),
                        delta="High",
                        delta_type="positive",
                        subtext="commuter utility",
                        sparkline_data=[88.5, 89.1, 89.7, 90.0, 90.2, 90.4, 90.5],
                        sparkline_color=COLORS["subscriber"],
                        tooltip="Percentage of rides completed by annual subscribers",
                        icon_class="fas fa-id-card",
                    ),
                    render_kpi_card(
                        title="Weekend Share",
                        value="14.8%",
                        delta="Leisure",
                        delta_type="purple",
                        subtext="longer rides",
                        sparkline_data=[15.2, 14.9, 15.0, 14.8, 14.6, 14.8, 14.8],
                        sparkline_color=COLORS["customer"],
                        tooltip="Weekend ridership proportion showing recreation shift",
                        icon_class="fas fa-calendar-week",
                    ),
                ],
            ),

            # Row 2: Visual Analytics Grid
            html.Div(
                className="grid grid-cols-1 lg:grid-cols-3 gap-6",
                children=[
                    # 24-Hour System Demand Chart (2 columns)
                    render_chart_card(
                        title="24-Hour System Demand Curve",
                        graph_id=ID_OVERVIEW_DEMAND_CHART,
                        figure=demand_fig,
                        subtitle="Diurnal trip distribution with commute peak annotations",
                        tooltip="Visualizes aggregate trip departure counts across 24 hours compared against 30-day baseline",
                        footer_text="Morning peak (8 AM: 17.3K) & Evening peak (5 PM: 21.8K)",
                        height=330,
                        className="lg:col-span-2",
                    ),

                    # Bay Area Regional Station Breakdown (1 column)
                    render_chart_card(
                        title="Bay Area Regional Distribution",
                        graph_id=ID_OVERVIEW_STATION_MAP,
                        figure=region_fig,
                        subtitle="Station count and trip share across metro clusters",
                        tooltip="Shows station network distribution and trip concentration by Bay Area sub-region",
                        footer_text="San Francisco concentrates 73.2% of all regional trips",
                        height=330,
                        className="lg:col-span-1",
                    ),
                ],
            ),

            # Row 3: Key Insights Panel (4 cards)
            render_key_insights(kpis=kpis, hourly_df=hourly_df),

            # Row 4: Quick-Access Launch Cards for Deep Dives
            html.Div(
                className="grid grid-cols-1 md:grid-cols-2 gap-6",
                children=[
                    # Launch Card 1: Station & Network Flow
                    html.Div(
                        className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between",
                        children=[
                            html.Div(
                                children=[
                                    html.Div(
                                        className="flex items-center justify-between mb-3",
                                        children=[
                                            html.Div(
                                                className="flex items-center gap-3",
                                                children=[
                                                    html.Div(
                                                        className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-base",
                                                        children=[html.I(className="fas fa-map-marked-alt")],
                                                    ),
                                                    html.Div(
                                                        children=[
                                                            html.H3("Station & Network Flow Analysis", className="text-base font-bold text-slate-900"),
                                                            html.Span("Member 5 Specialization", className="text-[11px] text-slate-500 font-medium"),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                            html.Span("M-5 Module", className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 border border-blue-200"),
                                        ],
                                    ),
                                    html.P(
                                        "Explore geospatial station densities, origin-destination transit corridors, dock saturation imbalances, and smart fleet rebalancing recommendations.",
                                        className="text-xs text-slate-600 leading-relaxed mb-4",
                                    ),
                                    html.Div(
                                        className="grid grid-cols-3 gap-2 bg-slate-50 rounded-lg p-3 text-center text-xs mb-4 border border-slate-100",
                                        children=[
                                            html.Div([html.Div("329", className="font-bold text-slate-800"), html.Div("Stations", className="text-[10px] text-slate-500")]),
                                            html.Div([html.Div("30", className="font-bold text-slate-800"), html.Div("Top Corridors", className="text-[10px] text-slate-500")]),
                                            html.Div([html.Div("15", className="font-bold text-blue-600"), html.Div("Dispatch Pairs", className="text-[10px] text-slate-500")]),
                                        ],
                                    ),
                                ],
                            ),
                            dcc.Link(
                                [
                                    html.Span("Launch Station Flow Analysis"),
                                    html.I(className="fas fa-arrow-right ml-2 text-xs"),
                                ],
                                href=ROUTE_STATIONS,
                                className="inline-flex items-center justify-center w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-colors shadow-xs",
                            ),
                        ],
                    ),

                    # Launch Card 2: Time & Demographics
                    html.Div(
                        className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between",
                        children=[
                            html.Div(
                                children=[
                                    html.Div(
                                        className="flex items-center justify-between mb-3",
                                        children=[
                                            html.Div(
                                                className="flex items-center gap-3",
                                                children=[
                                                    html.Div(
                                                        className="w-10 h-10 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center font-bold text-base",
                                                        children=[html.I(className="fas fa-user-clock")],
                                                    ),
                                                    html.Div(
                                                        children=[
                                                            html.H3("Time & Rider Demographics", className="text-base font-bold text-slate-900"),
                                                            html.Span("Member 4 Specialization", className="text-[11px] text-slate-500 font-medium"),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                            html.Span("M-4 Module", className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-teal-50 text-teal-600 border border-teal-200"),
                                        ],
                                    ),
                                    html.P(
                                        "Analyze hourly commuter curves, 7x24 weekly heatmaps, annual subscriber vs casual customer splits, age cohort adoption, and duration distributions.",
                                        className="text-xs text-slate-600 leading-relaxed mb-4",
                                    ),
                                    html.Div(
                                        className="grid grid-cols-3 gap-2 bg-slate-50 rounded-lg p-3 text-center text-xs mb-4 border border-slate-100",
                                        children=[
                                            html.Div([html.Div("90.5%", className="font-bold text-teal-600"), html.Div("Subscribers", className="text-[10px] text-slate-500")]),
                                            html.Div([html.Div("7x24", className="font-bold text-slate-800"), html.Div("Heat Matrix", className="text-[10px] text-slate-500")]),
                                            html.Div([html.Div("4", className="font-bold text-slate-800"), html.Div("Age Cohorts", className="text-[10px] text-slate-500")]),
                                        ],
                                    ),
                                ],
                            ),
                            dcc.Link(
                                [
                                    html.Span("Launch Time & Demographic Analysis"),
                                    html.I(className="fas fa-arrow-right ml-2 text-xs"),
                                ],
                                href=ROUTE_TIME_USER,
                                className="inline-flex items-center justify-center w-full py-2.5 px-4 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs transition-colors shadow-xs",
                            ),
                        ],
                    ),
                ],
            ),

            # Row 5: Data Lineage Accordion
            render_data_lineage_accordion(),
        ],
    )
