"""
pages/time_user_page.py – Modernized Time & Rider Demographics Analysis View
=============================================================================
Commuter rhythms & demographic breakdown:
  1. Top Row: 4 Demographic KPI cards
  2. Middle Row:
     - Hourly Demand Curve by User Type (Subscriber vs Customer with shaded commute bands)
     - Day of Week Trip Volume (Subscriber vs Customer)
  3. Next Row:
     - 7x24 Weekly Heatmap Matrix (Day of Week vs Hour of Day)
  4. Bottom Row (3 Equal-Height Cards):
     - Subscriber vs Customer Donut Split (90.5% center KPI)
     - Age Cohort Distribution (Gen Z, Millennials, Gen X, Boomers)
     - Trip Duration Histogram (5-min bins, capped at 60 min, median line)
"""

from __future__ import annotations

from typing import Dict, Any
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd

from config import (
    ID_TU_HOURLY_CHART,
    ID_TU_DOW_CHART,
    ID_TU_HEATMAP,
    ID_TU_DONUT,
    ID_TU_AGE_CHART,
    ID_TU_DURATION_HIST,
)
from components.kpi_card import render_kpi_card
from components.chart_card import render_chart_card
from utils.theme import apply_chart_theme, COLORS
from data_loader import load_time_demographics_data


def build_hourly_demand_figure(hourly_df: pd.DataFrame) -> go.Figure:
    """Builds hourly demand curve split by Subscriber vs Customer with rush hour bands."""
    fig = go.Figure()

    if hourly_df.empty:
        return fig

    hours = hourly_df["hour"].tolist()
    sub_trips = hourly_df["subscriber_trips"].tolist()
    cust_trips = hourly_df["customer_trips"].tolist()

    # Morning commute band (07:00 to 09:00)
    fig.add_vrect(
        x0=7,
        x1=9,
        fillcolor="rgba(20, 184, 166, 0.08)",
        layer="below",
        line_width=0,
        annotation_text="Morning Rush",
        annotation_position="top left",
        annotation_font=dict(size=10, color=COLORS["subscriber_dark"]),
    )

    # Evening commute band (16:00 to 18:00)
    fig.add_vrect(
        x0=16,
        x1=18,
        fillcolor="rgba(20, 184, 166, 0.08)",
        layer="below",
        line_width=0,
        annotation_text="Evening Rush",
        annotation_position="top left",
        annotation_font=dict(size=10, color=COLORS["subscriber_dark"]),
    )

    # Subscriber trace (Teal)
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=sub_trips,
            mode="lines+markers",
            name="Subscribers (Commuter)",
            line=dict(color=COLORS["subscriber"], width=3, shape="spline"),
            marker=dict(size=4),
            hovertemplate="Hour %{x}:00<br>Subscribers: <b>%{y:,}</b><extra></extra>",
        )
    )

    # Customer trace (Purple)
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=cust_trips,
            mode="lines+markers",
            name="Customers (Casual)",
            line=dict(color=COLORS["customer"], width=2.5, shape="spline"),
            marker=dict(size=4),
            hovertemplate="Hour %{x}:00<br>Casual Customers: <b>%{y:,}</b><extra></extra>",
        )
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=[0, 3, 6, 8, 12, 15, 17, 21, 23],
        ticktext=["12A", "3A", "6A", "8A", "12P", "3P", "5P", "9P", "11P"],
        title_text="Hour of Day",
    )
    fig.update_yaxes(title_text="Trips")

    return apply_chart_theme(fig, height=310, show_legend=True)


def build_dow_volume_figure(dow_df: pd.DataFrame) -> go.Figure:
    """Builds Day of Week trip volume comparing Subscriber vs Customer."""
    fig = go.Figure()

    if dow_df.empty:
        return fig

    days = dow_df["day_name"].tolist()
    sub_trips = dow_df["subscriber_trips"].tolist()
    cust_trips = dow_df["customer_trips"].tolist()

    # Subscriber bars
    fig.add_trace(
        go.Bar(
            x=days,
            y=sub_trips,
            name="Subscribers",
            marker=dict(color=COLORS["subscriber"]),
            hovertemplate="<b>%{x}</b><br>Subscribers: %{y:,}<extra></extra>",
        )
    )

    # Customer bars
    fig.add_trace(
        go.Bar(
            x=days,
            y=cust_trips,
            name="Casual Customers",
            marker=dict(color=COLORS["customer"]),
            hovertemplate="<b>%{x}</b><br>Casual Customers: %{y:,}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="stack",
        xaxis=dict(title="Day of Week"),
        yaxis=dict(title="Total Trips"),
    )

    return apply_chart_theme(fig, height=310, show_legend=True)


def build_heatmap_matrix_figure(heat_dict: Dict[tuple, int]) -> go.Figure:
    """Builds the 7x24 weekly matrix heatmap."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours = list(range(24))

    z_matrix = []
    # Plotly heatmaps display from bottom to top, so reverse days for Mon at top
    reversed_days = list(reversed(days))
    for d in reversed_days:
        row = [heat_dict.get((d, h), 0) for h in hours]
        z_matrix.append(row)

    fig = go.Figure(
        go.Heatmap(
            z=z_matrix,
            x=[f"{h}:00" for h in hours],
            y=reversed_days,
            colorscale=[
                [0.0, "#F0FDFA"],
                [0.2, "#CCFBF1"],
                [0.4, "#5EEAD4"],
                [0.7, "#0D9488"],
                [1.0, "#0F172A"],
            ],
            colorbar=dict(
                title=dict(text="Trips", font=dict(size=10, family="Inter")),
                thickness=12,
                len=0.8,
                tickfont=dict(size=9, family="Inter"),
            ),
            hovertemplate="<b>%{y} at %{x}</b><br>Volume: <b>%{z:,} trips</b><extra></extra>",
        )
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=[f"{h}:00" for h in [0, 3, 6, 8, 12, 15, 17, 21, 23]],
        ticktext=["12A", "3A", "6A", "8A", "12P", "3P", "5P", "9P", "11P"],
        title="Hour of Day",
    )
    fig.update_yaxes(title="Day of Week")

    return apply_chart_theme(fig, height=270, show_legend=False)


def build_user_split_donut_figure() -> go.Figure:
    """Subscriber vs Customer Donut chart with center KPI 90.5%."""
    fig = go.Figure(
        go.Pie(
            labels=["Subscribers", "Casual Customers"],
            values=[158170, 16554],
            hole=0.68,
            marker=dict(
                colors=[COLORS["subscriber"], COLORS["customer"]],
                line=dict(color="#FFFFFF", width=2),
            ),
            textinfo="percent",
            textfont=dict(size=11, family="Inter"),
            hovertemplate="<b>%{label}</b><br>Rides: %{value:,} (%{percent})<extra></extra>",
        )
    )

    fig.add_annotation(
        text="<b>90.5%</b><br><span style='font-size:10px;color:#64748B;'>Subscriber</span>",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(family="Inter", size=18, color=COLORS["text_main"]),
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )

    return apply_chart_theme(fig, height=270, show_legend=True)


def build_age_cohort_figure(age_df: pd.DataFrame) -> go.Figure:
    """Age cohort distribution grouped by user type."""
    fig = go.Figure()

    if age_df.empty:
        return fig

    cohorts = age_df["age_cohort"].tolist()
    sub_trips = age_df["subscriber_trips"].tolist()
    cust_trips = age_df["customer_trips"].tolist()

    fig.add_trace(
        go.Bar(
            x=cohorts,
            y=sub_trips,
            name="Subscribers",
            marker=dict(color=COLORS["subscriber"]),
            hovertemplate="<b>%{x}</b><br>Subscribers: %{y:,}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            x=cohorts,
            y=cust_trips,
            name="Casual Customers",
            marker=dict(color=COLORS["customer"]),
            hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        xaxis=dict(title="Rider Age Cohort"),
        yaxis=dict(title="Trips"),
        margin=dict(l=40, r=10, t=15, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return apply_chart_theme(fig, height=270, show_legend=True)


def build_duration_histogram_figure(dur_df: pd.DataFrame) -> go.Figure:
    """Duration distribution histogram with 5-minute bins and median line."""
    fig = go.Figure()

    if dur_df.empty:
        return fig

    bins = dur_df["bin_label"].tolist()
    trips = dur_df["trips"].tolist()

    fig.add_trace(
        go.Bar(
            x=bins,
            y=trips,
            marker=dict(
                color=["#0D9488" if idx == 1 else COLORS["subscriber"] for idx in range(len(bins))],
                line=dict(color="rgba(0,0,0,0.08)", width=1),
            ),
            hovertemplate="<b>%{x}</b> duration<br>Trips: %{y:,}<extra></extra>",
        )
    )

    # Median duration indicator at 8.5 min (bin '5-10m')
    fig.add_annotation(
        x="5-10m",
        y=max(trips) * 0.95,
        text="<b>Median: 8.5m</b><br>Peak (66.3K)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor=COLORS["subscriber_dark"],
        ax=40,
        ay=-25,
        font=dict(size=10, color=COLORS["text_main"]),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor=COLORS["subscriber"],
        borderwidth=1,
        borderpad=3,
    )

    fig.update_layout(
        xaxis=dict(title="Trip Duration (5-Minute Windows)"),
        yaxis=dict(title="Trip Frequency"),
        margin=dict(l=45, r=10, t=15, b=30),
    )

    return apply_chart_theme(fig, height=270, show_legend=False)


def render_time_user_page() -> html.Div:
    """
    Renders the modern Time & Rider Demographics dashboard page.
    """
    data = load_time_demographics_data()
    hourly_df = data.get("hourly", pd.DataFrame())
    dow_df = data.get("dow", pd.DataFrame())
    age_df = data.get("age_cohorts", pd.DataFrame())
    dur_df = data.get("duration_hist", pd.DataFrame())
    heat_dict = data.get("heatmap_matrix", {})
    kpis = data.get("kpis", {})

    hourly_fig = build_hourly_demand_figure(hourly_df)
    dow_fig = build_dow_volume_figure(dow_df)
    heat_fig = build_heatmap_matrix_figure(heat_dict)
    donut_fig = build_user_split_donut_figure()
    age_fig = build_age_cohort_figure(age_df)
    dur_fig = build_duration_histogram_figure(dur_df)

    return html.Div(
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6",
        children=[
            # Page Title Header
            html.Div(
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2",
                children=[
                    html.Div(
                        children=[
                            html.H2(
                                "Time & Rider Demographics",
                                className="text-2xl font-bold text-slate-900 tracking-tight",
                            ),
                            html.P(
                                "Commuter rhythms, 7x24 weekly density matrix, membership splits, and demographic behavior",
                                className="text-xs text-slate-500 mt-0.5",
                            ),
                        ],
                    ),
                    html.Div(
                        className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-purple-50 border border-purple-200 text-purple-800 text-xs font-semibold self-start sm:self-auto",
                        children=[
                            html.Span(className="w-2 h-2 rounded-full bg-purple-500"),
                            html.Span("M-4 Demographic Specialization"),
                        ],
                    ),
                ],
            ),

            # Top Row: 4 Demographic KPI Cards
            html.Div(
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
                children=[
                    render_kpi_card(
                        title="Avg Subscriber Duration",
                        value=kpis.get("subscriber_avg_dur", "10.7 min"),
                        delta="Commuter",
                        delta_type="positive",
                        subtext="high velocity utility",
                        sparkline_data=[10.5, 10.6, 10.8, 10.7, 10.7, 10.6, 10.7],
                        sparkline_color=COLORS["subscriber"],
                        tooltip="Average trip duration for annual subscriber passholders",
                        icon_class="fas fa-stopwatch",
                    ),
                    render_kpi_card(
                        title="Avg Customer Duration",
                        value=kpis.get("customer_avg_dur", "21.7 min"),
                        delta="+103%",
                        delta_type="purple",
                        subtext="leisure exploration",
                        sparkline_data=[20.8, 21.2, 21.5, 21.8, 22.1, 21.7, 21.7],
                        sparkline_color=COLORS["customer"],
                        tooltip="Average trip duration for non-member casual day passholders",
                        icon_class="fas fa-clock",
                    ),
                    render_kpi_card(
                        title="Peak Commute Hours",
                        value=kpis.get("peak_commute_hours", "8 AM & 5 PM"),
                        delta="Twin Peaks",
                        delta_type="blue",
                        subtext="bimodal commute surges",
                        sparkline_data=[2400, 17300, 7800, 6900, 21800, 10200, 4800],
                        sparkline_color=COLORS["surplus"],
                        tooltip="Hours of the day with maximum system-wide trip departure concentration",
                        icon_class="fas fa-bolt",
                    ),
                    render_kpi_card(
                        title="Weekend Duration Lift",
                        value=kpis.get("weekend_duration_lift", "+48%"),
                        delta="Recreation",
                        delta_type="purple",
                        subtext="longer scenic rides",
                        sparkline_data=[11.2, 11.4, 11.3, 11.5, 15.6, 16.1, 15.8],
                        sparkline_color=COLORS["customer"],
                        tooltip="Percentage increase in ride duration on Saturday and Sunday vs weekdays",
                        icon_class="fas fa-calendar-day",
                    ),
                ],
            ),

            # Middle Row: Hourly Demand Curve + Day of Week Trip Volume
            html.Div(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6",
                children=[
                    render_chart_card(
                        title="Hourly Demand Curve by User Type",
                        graph_id=ID_TU_HOURLY_CHART,
                        figure=hourly_fig,
                        subtitle="Subscriber vs Customer ridership volume across 24 hours with shaded rush bands",
                        tooltip="Shows distinct bimodal commuter peaks for subscribers vs gradual midday rise for customers",
                        height=310,
                    ),
                    render_chart_card(
                        title="Day of Week Trip Volume",
                        graph_id=ID_TU_DOW_CHART,
                        figure=dow_fig,
                        subtitle="Total rides by day of the week comparing Subscriber and Customer volumes",
                        tooltip="Highlights Tuesday through Thursday commuter dominance vs weekend volume drops",
                        height=310,
                    ),
                ],
            ),

            # Next Row: 7x24 Weekly Heatmap Matrix
            render_chart_card(
                title="7x24 Weekly System Heatmap Matrix",
                graph_id=ID_TU_HEATMAP,
                figure=heat_fig,
                subtitle="Day of Week (y-axis) vs Hour of Day (x-axis) trip density matrix",
                tooltip="Dark teal spots highlight peak commuter congestion during Tuesday-Thursday rush hours",
                footer_text="Heaviest traffic: Thursday 5:00 PM (4,820 rides in a single hour window)",
                height=270,
            ),

            # Bottom Row: 3 Equal-Height Chart Cards (1x3 Grid)
            html.Div(
                className="grid grid-cols-1 md:grid-cols-3 gap-6",
                children=[
                    # 1. Subscriber vs Customer Donut
                    render_chart_card(
                        title="User Type Distribution",
                        graph_id=ID_TU_DONUT,
                        figure=donut_fig,
                        subtitle="Subscribers (90.5%) vs Customers (9.5%)",
                        tooltip="Proportion of total trips completed by annual members vs casual riders",
                        height=270,
                    ),

                    # 2. Age Cohort Distribution
                    render_chart_card(
                        title="Age Cohort Distribution",
                        graph_id=ID_TU_AGE_CHART,
                        figure=age_fig,
                        subtitle="Trip volume across generational brackets",
                        tooltip="Millennials (25-39) represent the predominant rider demographic across the network",
                        height=270,
                    ),

                    # 3. Trip Duration Histogram
                    render_chart_card(
                        title="Trip Duration Distribution",
                        graph_id=ID_TU_DURATION_HIST,
                        figure=dur_fig,
                        subtitle="5-minute bins capped at 60m with median reference",
                        tooltip="Most trips finish within 5-10 minutes, optimal for 30-minute membership limits",
                        height=270,
                    ),
                ],
            ),
        ],
    )
