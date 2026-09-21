"""
pages/user_trips_page.py – Member 3: Rider & Trip Behavior Dynamics View
========================================================================
Presents Member 3's complete analytical suite (users-trip-analysis) matching the
enterprise SaaS UI of the Ford GoBike Master Analytics Platform:
  - 4 Executive KPI Cards: Total Trips, Gender Split, Avg Duration Gap, Top Hub Station
  - 4 Interactive Analytical Charts:
      * Chart 1: Trips by Gender & Membership Split (Grouped Bar)
      * Chart 2: Average Duration Rhythm Across 24 Hours (Line with Markers)
      * Chart 3: Trip Duration by User Type (Bar Chart)
      * Chart 4: Daily Trip Velocity Trajectory (Area Trend)
  - Fully reactive to the 4 Global Filters (Rider Type, Region, Gender, Day Type)
"""

from __future__ import annotations

import time
from time import perf_counter
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc, Input, Output

from config import (
    ID_GLOBAL_STORE,
    GLOBAL_FILTER_DEFAULTS,
)
from utils.metrics_calculator import (
    calc_total_trips,
    calc_subscriber_pct,
    calc_mean_duration,
    calc_duration_by_user_type,
    to_display_user_type,
    DEFAULT_KPIS,
)

# ---------------------------------------------------------------------------
# Phase 5: In-memory filtered-data cache keyed by filter tuple
# ---------------------------------------------------------------------------
_FILTERED_DATA_CACHE: dict[tuple, pd.DataFrame] = {}


def _filter_key(filter_data: dict | None) -> tuple:
    """Stable hashable key derived from the 4 filter dimensions."""
    if not filter_data:
        return ("All", "All", "All", "All")
    return (
        filter_data.get("user_type", "All"),
        filter_data.get("region", "All"),
        filter_data.get("gender", "All"),
        filter_data.get("day_type", "All"),
    )


def _get_filtered_cached(df: pd.DataFrame, filter_data: dict | None) -> pd.DataFrame:
    """Return filtered dataframe from cache when the same filter key was already computed."""
    key = _filter_key(filter_data)
    if key in _FILTERED_DATA_CACHE:
        return _FILTERED_DATA_CACHE[key]
    filtered = filter_m3_data(df, filter_data)
    _FILTERED_DATA_CACHE[key] = filtered
    return filtered


def _phase5_profiler(label: str, fn, *args, **kwargs):
    """Thin timing wrapper used by the callback to measure individual build steps."""
    t0 = perf_counter()
    result = fn(*args, **kwargs)
    ms = (perf_counter() - t0) * 1000
    print(f"   [PHASE5-PROF] {label:<42} {ms:>7.1f} ms", flush=True)
    return result


def filter_m3_data(df: pd.DataFrame, filter_data: dict | None) -> pd.DataFrame:
    """Apply global filter dimensions to Member 3 user trips dataframe."""
    if not filter_data or df.empty:
        return df

    filtered = df
    user_type = filter_data.get("user_type", "All")
    region = filter_data.get("region", "All")
    gender = filter_data.get("gender", "All")
    day_type = filter_data.get("day_type", "All")

    if user_type != "All" and "user_type" in filtered.columns:
        filtered = filtered[filtered["user_type"] == user_type]

    if gender != "All" and "member_gender" in filtered.columns:
        filtered = filtered[filtered["member_gender"] == gender]

    if day_type == "Weekday" and "weekend_flag" in filtered.columns:
        filtered = filtered[filtered["weekend_flag"] == 0]
    elif day_type == "Weekend" and "weekend_flag" in filtered.columns:
        filtered = filtered[filtered["weekend_flag"] == 1]

    if region != "All" and "region" in filtered.columns:
        filtered = filtered[filtered["region"] == region]

    return filtered


def _create_gender_user_chart(df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart showing trips broken down by User Type and Gender with value labels on all bars."""
    if df.empty or "user_type" not in df.columns or "member_gender" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig

    valid = df.dropna(subset=["user_type", "member_gender"]).copy()
    if valid.empty:
        fig = go.Figure()
        fig.update_layout(title="No records matching filter")
        return fig

    valid["display_user"] = [to_display_user_type(u) for u in valid["user_type"]]
    grp = valid.groupby(["display_user", "member_gender"], observed=True).size().reset_index(name="trips")

    color_map = {
        "Male": "#14B8A6",     # Teal
        "Female": "#A855F7",   # Purple
        "Other": "#F59E0B",    # Amber
    }

    fig = go.Figure()
    user_categories = ["Subscriber", "Casual"]
    for g in ["Male", "Female", "Other"]:
        sub = grp[grp["member_gender"] == g].copy()
        existing_users = set(sub["display_user"])
        for u in user_categories:
            if u not in existing_users and u in valid["display_user"].unique():
                sub = pd.concat([sub, pd.DataFrame([{"display_user": u, "member_gender": g, "trips": 0}])], ignore_index=True)
        sub = sub.sort_values("display_user", ascending=False)

        if not sub.empty:
            bar_texts = [
                f"{v/1000:.1f}k" if v >= 1000 else (f"{v:,}" if v > 0 else "")
                for v in sub["trips"]
            ]
            fig.add_trace(
                go.Bar(
                    name=g,
                    x=sub["display_user"],
                    y=sub["trips"],
                    marker=dict(color=color_map.get(g, "#64748B")),
                    text=bar_texts,
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(color="#0F172A", size=10.5, family="Inter"),
                    hovertemplate="<b>%{x}</b> (%{data.name})<br>Trips: <b>%{y:,}</b><extra></extra>",
                )
            )

    max_val = grp["trips"].max() if not grp.empty else 1000
    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.1,
        margin=dict(l=20, r=20, t=25, b=30),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(color="#64748B", size=11, family="Inter")),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            tickformat=",",
            tickfont=dict(color="#64748B", size=10, family="Inter"),
            range=[0, max_val * 1.22],
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#64748B")),
    )
    return fig


def _create_hour_duration_chart(df: pd.DataFrame) -> go.Figure:
    """Average trip duration across 24 hours, annotating small sample outliers (n < 50 trips)."""
    if df.empty or "hour" not in df.columns or "duration_min" not in df.columns:
        fig = go.Figure()
        return fig

    grp = df.groupby("hour", observed=True).agg(
        avg_duration=("duration_min", "mean"),
        trip_count=("duration_min", "count")
    ).reset_index().sort_values("hour")

    marker_colors = ["#94A3B8" if cnt < 50 else "#0D9488" for cnt in grp["trip_count"]]
    marker_sizes = [7 if cnt < 50 else 6 for cnt in grp["trip_count"]]
    hover_texts = [
        f"<b>{int(h):02d}:00</b><br>"
        f"Avg Duration: <b>{dur:.1f} min</b><br>"
        f"Sample Size: <b>{cnt:,} trips</b>"
        + ("<br><span style='color:#F97316;font-size:10px;'>* Low sample size (<50 trips)</span>" if cnt < 50 else "")
        for h, dur, cnt in zip(grp["hour"], grp["avg_duration"], grp["trip_count"])
    ]

    fig = go.Figure(
        go.Scatter(
            x=grp["hour"],
            y=grp["avg_duration"],
            mode="lines+markers",
            line=dict(color="#14B8A6", width=2.5, shape="spline"),
            marker=dict(
                size=marker_sizes,
                color=marker_colors,
                line=dict(color="#FFFFFF", width=1.5),
            ),
            fill="tozeroy",
            fillcolor="rgba(20, 184, 166, 0.08)",
            hovertext=hover_texts,
            hoverinfo="text",
        )
    )

    # Annotate outlier / low sample spike if present (e.g. 3 AM)
    low_sample = grp[grp["trip_count"] < 50]
    annotations = []
    if not low_sample.empty:
        spike_row = low_sample.loc[low_sample["avg_duration"].idxmax()]
        annotations.append(
            dict(
                x=spike_row["hour"],
                y=spike_row["avg_duration"],
                text=f"3 AM Spike (n={int(spike_row['trip_count'])})<br><span style='font-size:8.5px;'>Outlier due to small sample</span>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor="#F97316",
                ax=30,
                ay=-35,
                font=dict(size=9.5, color="#C2410C", family="Inter"),
                bgcolor="#FFF7ED",
                bordercolor="#FDBA74",
                borderwidth=1,
                borderpad=3,
            )
        )

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=30),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=annotations,
        xaxis=dict(
            tickmode="linear",
            tick0=0,
            dtick=2,
            ticksuffix=":00",
            showgrid=False,
            tickfont=dict(color="#64748B", size=10, family="Inter"),
        ),
        yaxis=dict(
            ticksuffix=" m",
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(color="#64748B", size=10, family="Inter"),
        ),
    )
    return fig


def _create_user_duration_chart(df: pd.DataFrame) -> go.Figure:
    """Bar comparison of average duration between Subscribers and Customers."""
    if df.empty or "user_type" not in df.columns or "duration_min" not in df.columns:
        return go.Figure()

    grp = df.groupby("user_type", observed=True)["duration_min"].mean().reset_index()
    grp["display_user"] = [to_display_user_type(u) for u in grp["user_type"]]

    colors = ["#A855F7" if u in ("Customer", "Casual") else "#14B8A6" for u in grp["user_type"]]
    fig = go.Figure(
        go.Bar(
            x=grp["display_user"],
            y=grp["duration_min"],
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{v:.1f} min" for v in grp["duration_min"]],
            textposition="auto",
            textfont=dict(color="#FFFFFF", size=12, family="Inter"),
            width=0.45,
            hovertemplate="<b>%{x}</b><br>Avg Duration: <b>%{y:.2f} min</b><extra></extra>",
        )
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=30),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(color="#64748B", size=11, family="Inter")),
        yaxis=dict(ticksuffix=" m", showgrid=True, gridcolor="#F1F5F9", tickfont=dict(color="#64748B", size=10, family="Inter")),
    )
    return fig


def _create_daily_trip_chart(df: pd.DataFrame) -> go.Figure:
    """Daily ridership volume trajectory."""
    if df.empty or "day_of_week" not in df.columns:
        return go.Figure()

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    counts = df["day_of_week"].value_counts().reindex(days_order, fill_value=0)

    colors = ["#14B8A6" if d not in ("Saturday", "Sunday") else "#A855F7" for d in days_order]
    fig = go.Figure(
        go.Bar(
            x=[d[:3] for d in days_order],
            y=counts.values,
            marker=dict(color=colors),
            text=[f"{v/1000:.1f}k" if v >= 1000 else f"{v}" for v in counts.values],
            textposition="auto",
            textfont=dict(color="#FFFFFF", size=11, family="Inter"),
            hovertemplate="<b>%{x}</b><br>Trips: <b>%{y:,}</b><extra></extra>",
        )
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=30),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(color="#64748B", size=11, family="Inter")),
        yaxis=dict(tickformat=",", showgrid=True, gridcolor="#F1F5F9", tickfont=dict(color="#64748B", size=10, family="Inter")),
    )
    return fig


def render_user_trips_page() -> html.Div:
    """Builds the complete Member 3 view."""
    # Fast in-memory cached load
    from utils.module_loader import load_clean_time_user_data
    df = load_clean_time_user_data()

    dur_metrics = calc_duration_by_user_type(df)
    total_trips = calc_total_trips(df)
    sub_pct = calc_subscriber_pct(df, total_trips=total_trips)

    male_count = len(df[df["member_gender"] == "Male"]) if "member_gender" in df.columns else 0
    male_pct = (male_count / max(1, total_trips)) * 100

    avg_dur = calc_mean_duration(df)

    fig1 = _create_gender_user_chart(df)
    fig2 = _create_hour_duration_chart(df)
    fig3 = _create_user_duration_chart(df)
    fig4 = _create_daily_trip_chart(df)

    return html.Div(
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col gap-6",
        children=[
            # ── 1. Headline 4 KPI Cards ──────────────────────────────────
            html.Section(
                className="grid grid-cols-2 lg:grid-cols-4 gap-4",
                children=[
                    html.Div(
                        className="analytics-card p-4 flex flex-col justify-between bg-white rounded-xl border border-slate-200 shadow-2xs",
                        children=[
                            html.Span("Total Analyzed Trips", className="text-xs font-medium text-slate-500"),
                            html.Div(f"{total_trips:,}", id="m3-kpi-total-trips", className="text-2xl font-black text-slate-900 tracking-tight my-1"),
                            html.Span("Overall Network", className="text-[11px] font-semibold text-teal-600"),
                        ],
                    ),
                    html.Div(
                        className="analytics-card p-4 flex flex-col justify-between bg-white rounded-xl border border-slate-200 shadow-2xs",
                        children=[
                            html.Span("Male Rider Share", className="text-xs font-medium text-slate-500"),
                            html.Div(f"{male_pct:.1f}%", id="m3-kpi-male-pct", className="text-2xl font-black text-teal-600 tracking-tight my-1"),
                            html.Span("Primary commuter base", className="text-[11px] font-medium text-slate-400"),
                        ],
                    ),
                    html.Div(
                        className="analytics-card p-4 flex flex-col justify-between bg-white rounded-xl border border-slate-200 shadow-2xs",
                        children=[
                            html.Span("Subscriber Ratio", className="text-xs font-medium text-slate-500"),
                            html.Div(f"{sub_pct:.1f}%", id="m3-kpi-sub-pct", className="text-2xl font-black text-purple-600 tracking-tight my-1"),
                            html.Span("High recurring loyalty", className="text-[11px] font-medium text-slate-400"),
                        ],
                    ),
                    html.Div(
                        className="analytics-card p-4 flex flex-col justify-between bg-white rounded-xl border border-slate-200 shadow-2xs",
                        children=[
                            html.Span("Overall Avg Duration", className="text-xs font-medium text-slate-500"),
                            html.Div(f"{avg_dur:.1f} min", id="m3-kpi-avg-dur", className="text-2xl font-black text-slate-900 tracking-tight my-1"),
                            html.Span(f"Casual: ~{dur_metrics['casual_mean']:.1f}m | Sub: ~{dur_metrics['subscriber_mean']:.1f}m", className="text-[11px] font-medium text-slate-400"),
                        ],
                    ),
                ],
            ),

            # ── 2. Row 1: Gender & Hourly Duration ────────────────────────
            html.Section(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6",
                children=[
                    html.Div(
                        className="analytics-card p-5 bg-white rounded-xl border border-slate-200 shadow-2xs",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-3",
                                children=[
                                    html.Div([
                                        html.H3("Trips by Gender & Membership Split", className="text-sm font-bold text-slate-900"),
                                        html.P("Subscriber vs Casual counts segmented across gender profiles", className="text-xs text-slate-400 mt-0.5"),
                                    ]),
                                    html.Span("Gender Matrix", className="text-[11px] font-bold text-teal-600 bg-teal-50 px-2 py-0.5 rounded"),
                                ],
                            ),
                            dcc.Graph(id="m3-gender-user-chart", figure=fig1, config={"displayModeBar": False}),
                        ],
                    ),
                    html.Div(
                        className="analytics-card p-5 bg-white rounded-xl border border-slate-200 shadow-2xs",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-3",
                                children=[
                                    html.Div([
                                        html.H3("Average Duration by Start Hour", className="text-sm font-bold text-slate-900"),
                                        html.P("Rhythm of trip lengths across the 24-hour daily cycle", className="text-xs text-slate-400 mt-0.5"),
                                    ]),
                                    html.Span("Hourly Rhythm", className="text-[11px] font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded"),
                                ],
                            ),
                            dcc.Graph(id="m3-hour-duration-chart", figure=fig2, config={"displayModeBar": False}),
                        ],
                    ),
                ],
            ),

            # ── 3. Row 2: Duration by User Type & Day of Week ─────────────
            html.Section(
                className="grid grid-cols-1 lg:grid-cols-2 gap-6",
                children=[
                    html.Div(
                        className="analytics-card p-5 bg-white rounded-xl border border-slate-200 shadow-2xs",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-3",
                                children=[
                                    html.Div([
                                        html.H3("Duration Comparison by User Type", className="text-sm font-bold text-slate-900"),
                                        html.P(f"Casual riders average {dur_metrics['ratio_str']} longer trip duration than Subscribers", className="text-xs text-slate-400 mt-0.5"),
                                    ]),
                                    html.Span("User Duration", className="text-[11px] font-bold text-teal-600 bg-teal-50 px-2 py-0.5 rounded"),
                                ],
                            ),
                            dcc.Graph(id="m3-user-duration-chart", figure=fig3, config={"displayModeBar": False}),
                        ],
                    ),
                    html.Div(
                        className="analytics-card p-5 bg-white rounded-xl border border-slate-200 shadow-2xs",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-3",
                                children=[
                                    html.Div([
                                        html.H3("Day of Week Ridership Trajectory", className="text-sm font-bold text-slate-900"),
                                        html.P("Weekday volume peaks vs weekend recreation levels", className="text-xs text-slate-400 mt-0.5"),
                                    ]),
                                    html.Span("Weekly Volume", className="text-[11px] font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded"),
                                ],
                            ),
                            dcc.Graph(id="m3-daily-trip-chart", figure=fig4, config={"displayModeBar": False}),
                        ],
                    ),
                ],
            ),
        ],
    )


def register_user_trips_callbacks(app) -> None:
    """Register reactive filtering callback for Member 3 user trips view."""
    @app.callback(
        [
            Output("m3-kpi-total-trips", "children"),
            Output("m3-kpi-male-pct", "children"),
            Output("m3-kpi-sub-pct", "children"),
            Output("m3-kpi-avg-dur", "children"),
            Output("m3-gender-user-chart", "figure"),
            Output("m3-hour-duration-chart", "figure"),
            Output("m3-user-duration-chart", "figure"),
            Output("m3-daily-trip-chart", "figure"),
        ],
        [Input(ID_GLOBAL_STORE, "data")],
    )
    def update_user_trips(filter_data: dict | None):
        _cb_start = perf_counter()
        from utils.module_loader import load_clean_time_user_data

        # Phase 5: load from lru_cache (never re-queries Supabase)
        df = load_clean_time_user_data()

        # Phase 5: filter slice from in-memory cache (never re-filters same tuple)
        filtered = _get_filtered_cached(df, filter_data)

        total_trips = calc_total_trips(filtered)
        sub_pct = calc_subscriber_pct(filtered, total_trips=total_trips)

        male_count = len(filtered[filtered["member_gender"] == "Male"]) if "member_gender" in filtered.columns else 0
        male_pct = (male_count / max(1, total_trips)) * 100

        avg_dur = calc_mean_duration(filtered)

        # Phase 5: profile each chart build independently
        fig1 = _phase5_profiler("gender_user_chart", _create_gender_user_chart, filtered)
        fig2 = _phase5_profiler("hour_duration_chart", _create_hour_duration_chart, filtered)
        fig3 = _phase5_profiler("user_duration_chart", _create_user_duration_chart, filtered)
        fig4 = _phase5_profiler("daily_trip_chart", _create_daily_trip_chart, filtered)

        _total_ms = (perf_counter() - _cb_start) * 1000
        print(f"   [PHASE5-PROF] update_user_trips TOTAL: {_total_ms:.1f} ms  "
              f"(filter={_filter_key(filter_data)}, rows={len(filtered):,})", flush=True)

        return (
            f"{total_trips:,}",
            f"{male_pct:.1f}%",
            f"{sub_pct:.1f}%",
            f"{avg_dur:.1f} min",
            fig1,
            fig2,
            fig3,
            fig4,
        )

