"""
charts/time_analysis.py – Temporal Usage & Duration Visualizations
====================================================================
Plotly chart generators styled with the Tailwind aesthetic used across
the other chart modules (station_analysis.py / trip_analysis.py):

  1. Trips by Hour of Day (smooth line, single series)
  2. Day-of-Week × Hour Heatmap (demand intensity matrix)
  3. Average Trip Duration by Hour (line, minute scale)
  4. Weekday vs Weekend Average Duration (two-bar comparison)

Column mapping (CSV → internal):
  - "hour"          → used for hourly analyses (T1, T3, and heatmap columns)
  - "day"           → available in CSV; not used by these 4 charts directly
  - "day_of_week"   → used for the Day × Hour heatmap rows
  - "duration_min"  → used for both duration charts
  - weekend_flag    → derived internally from day_of_week (no CSV column needed)

Design notes:
  - All functions return go.Figure.
  - Empty inputs return empty_figure() with a context-appropriate message.
  - Strict ordering: hours 0..23, days Monday..Sunday.
  - Dark hoverlabel card matching the rest of the dashboard.
  - Peak hour is derived from the data at runtime, not assumed.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_LINE, CHART_HEIGHT_HEATMAP
from utils.theme import apply_chart_theme, empty_figure


# Canonical day ordering (matches EDA notebook)
_DAY_ORDER = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",
]

# Weekend days for deriving weekend_flag from day_of_week
_WEEKEND_DAYS = {"Saturday", "Sunday"}


def _normalize_day_names(series: pd.Series) -> pd.Series:
    """
    Normalize day_of_week values to Title Case (e.g. "monday" → "Monday")
    so they match _DAY_ORDER regardless of the source CSV's casing.
    """
    return series.astype(str).str.strip().str.title()


# ---------------------------------------------------------------------------
# 1. Trips by Hour of Day
# ---------------------------------------------------------------------------

def create_trips_by_hour_chart(df: pd.DataFrame) -> go.Figure:
    """
    Line chart of total trips per start hour (0–23).

    Uses the CSV `hour` column.
    """
    if df.empty or "hour" not in df.columns:
        return empty_figure("No temporal data available for the selected filters.",
                            height=CHART_HEIGHT_LINE)

    trips_by_hour = (
        df.groupby("hour")
          .size()
          .reindex(range(24), fill_value=0)
    )

    if trips_by_hour.sum() == 0:
        return empty_figure("No trips recorded in the selected filter scope.",
                            height=CHART_HEIGHT_LINE)

    peak_hour = int(trips_by_hour.idxmax())
    peak_val = int(trips_by_hour.max())

    hover_texts = [
        f"<b>{h:02d}:00 – {h:02d}:59</b><br>"
        f"Trips: <b>{v:,}</b>"
        + (" <span style='color:#10b981;'>← Peak</span>" if h == peak_hour else "")
        for h, v in zip(trips_by_hour.index, trips_by_hour.values)
    ]

    fig = go.Figure(
        go.Scatter(
            x=trips_by_hour.index,
            y=trips_by_hour.values,
            mode="lines+markers",
            line=dict(color=COLORS["accent_teal"], width=2.5, shape="spline"),
            marker=dict(
                size=7,
                color=COLORS["accent_teal"],
                line=dict(color="#ffffff", width=1.5),
            ),
            hovertext=hover_texts,
            hoverinfo="text",
            name="Trips",
        )
    )

    # Subtle halo marker on the peak hour (data-driven)
    fig.add_trace(
        go.Scatter(
            x=[peak_hour],
            y=[peak_val],
            mode="markers",
            marker=dict(
                size=14,
                color="rgba(16, 185, 129, 0.25)",
                line=dict(color=COLORS["accent_teal"], width=2),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_LINE,
        margin=dict(l=10, r=20, t=10, b=30),
    )

    fig.update_layout(
        xaxis=dict(
            title="",
            tickmode="array",
            tickvals=list(range(0, 24, 2)),
            ticktext=[f"{h:02d}" for h in range(0, 24, 2)],
            showgrid=False,
            range=[-0.5, 23.5],
        ),
        yaxis=dict(
            title="",
            tickformat=",",
            showgrid=True,
            gridcolor="#f1f5f9",
            rangemode="tozero",
        ),
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# 2. Day-of-Week × Hour Heatmap
# ---------------------------------------------------------------------------

def create_day_hour_heatmap_chart(df: pd.DataFrame) -> go.Figure:
    """
    Heatmap of trip demand by day of week (rows) and hour of day (columns).

    Uses CSV `day_of_week` for rows and `hour` for columns.
    Day names are normalized to Title Case to match the canonical ordering.
    """
    if df.empty or "day_of_week" not in df.columns or "hour" not in df.columns:
        return empty_figure("No temporal data available for the selected filters.",
                            height=CHART_HEIGHT_HEATMAP)

    df_local = df.copy()
    df_local["_day_norm"] = _normalize_day_names(df_local["day_of_week"])

    matrix = (
        df_local.groupby(["_day_norm", "hour"])
                .size()
                .unstack(fill_value=0)
                .reindex(_DAY_ORDER, fill_value=0)
                .reindex(columns=range(24), fill_value=0)
    )

    if matrix.values.sum() == 0:
        return empty_figure("No trips recorded in the selected filter scope.",
                            height=CHART_HEIGHT_HEATMAP)

    z = matrix.values
    hover_texts = [
        [
            f"<b>{day}</b> at <b>{h:02d}:00</b><br>Trips: <b>{int(v):,}</b>"
            for h, v in enumerate(row)
        ]
        for day, row in zip(matrix.index, z)
    ]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=list(range(24)),
            y=matrix.index.tolist(),
            colorscale=[
                [0.0, "#f8fafc"],
                [0.25, "#bfdbfe"],
                [0.55, "#3b82f6"],
                [0.8, "#1e40af"],
                [1.0, "#0f172a"],
            ],
            hovertemplate="%{text}<extra></extra>",
            text=hover_texts,
            showscale=True,
            colorbar=dict(
                title=dict(text="Trips", font=dict(size=10, color="#475569")),
                thickness=10,
                len=0.75,
                tickfont=dict(size=9, color="#64748b"),
                outlinewidth=0,
            ),
            xgap=1,
            ygap=1,
        )
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_HEATMAP,
        margin=dict(l=10, r=10, t=10, b=30),
    )

    fig.update_layout(
        xaxis=dict(
            title="",
            tickmode="array",
            tickvals=list(range(0, 24, 2)),
            ticktext=[f"{h:02d}" for h in range(0, 24, 2)],
            showgrid=False,
            side="bottom",
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            autorange="reversed",  # Monday at top
            tickfont=dict(color="#334155", size=11, family="Inter"),
        ),
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# 3. Average Trip Duration by Hour
# ---------------------------------------------------------------------------

def create_avg_duration_by_hour_chart(df: pd.DataFrame) -> go.Figure:
    """
    Line chart of average trip duration (minutes) per start hour (0–23).

    Uses CSV `hour` + `duration_min`.
    """
    if df.empty or "hour" not in df.columns or "duration_min" not in df.columns:
        return empty_figure("No duration data available for the selected filters.",
                            height=CHART_HEIGHT_LINE)

    avg_dur = (
        df.groupby("hour")["duration_min"]
          .mean()
          .reindex(range(24))
    )

    # Drop hours with no trips (NaN) so the line doesn't dip to 0 artificially
    plot_data = avg_dur.dropna()

    if plot_data.empty:
        return empty_figure("No duration data available for the selected filter scope.",
                            height=CHART_HEIGHT_LINE)

    peak_hour = int(plot_data.idxmax())
    peak_val = float(plot_data.max())

    hover_texts = [
        f"<b>{h:02d}:00 – {h:02d}:59</b><br>"
        f"Avg Duration: <b>{v:.1f} min</b>"
        for h, v in zip(plot_data.index, plot_data.values)
    ]

    fig = go.Figure(
        go.Scatter(
            x=plot_data.index,
            y=plot_data.values,
            mode="lines+markers",
            line=dict(color=COLORS["accent_purple"], width=2.5, shape="spline"),
            marker=dict(
                size=7,
                color=COLORS["accent_purple"],
                line=dict(color="#ffffff", width=1.5),
            ),
            hovertext=hover_texts,
            hoverinfo="text",
            name="Avg Duration",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[peak_hour],
            y=[peak_val],
            mode="markers",
            marker=dict(
                size=14,
                color="rgba(168, 85, 247, 0.25)",
                line=dict(color=COLORS["accent_purple"], width=2),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_LINE,
        margin=dict(l=10, r=20, t=10, b=30),
    )

    fig.update_layout(
        xaxis=dict(
            title="",
            tickmode="array",
            tickvals=list(range(0, 24, 2)),
            ticktext=[f"{h:02d}" for h in range(0, 24, 2)],
            showgrid=False,
            range=[-0.5, 23.5],
        ),
        yaxis=dict(
            title="",
            ticksuffix=" min",
            showgrid=True,
            gridcolor="#f1f5f9",
            rangemode="tozero",
        ),
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# 4. Weekday vs Weekend Average Duration
# ---------------------------------------------------------------------------

def create_weekday_vs_weekend_duration_chart(df: pd.DataFrame) -> go.Figure:
    """
    Two-bar comparison of average trip duration on weekdays vs weekends.

    Uses CSV `day_of_week` + `duration_min`.
    `weekend_flag` is derived internally from `day_of_week`
    (Saturday / Sunday → Weekend; the rest → Weekday).
    """
    if df.empty or "day_of_week" not in df.columns or "duration_min" not in df.columns:
        return empty_figure("No duration data available for the selected filters.",
                            height=CHART_HEIGHT_LINE)

    df_local = df.copy()
    df_local["_day_norm"] = _normalize_day_names(df_local["day_of_week"])
    df_local["_is_weekend"] = df_local["_day_norm"].isin(_WEEKEND_DAYS)

    grouped = df_local.groupby("_is_weekend")["duration_min"].mean()

    weekday_val = float(grouped.get(False, 0.0))
    weekend_val = float(grouped.get(True, 0.0))

    if weekday_val == 0.0 and weekend_val == 0.0:
        return empty_figure("No duration data available for the selected filter scope.",
                            height=CHART_HEIGHT_LINE)

    labels = ["Weekday", "Weekend"]
    values = [weekday_val, weekend_val]
    colors = [
        "rgba(13, 148, 136, 0.85)",   # teal (weekday)
        "rgba(168, 85, 247, 0.85)",   # purple (weekend)
    ]
    borders = ["#0f766e", "#9333ea"]

    hover_texts = [
        f"<b>{lbl}</b><br>Avg Duration: <b>{v:.2f} min</b>"
        for lbl, v in zip(labels, values)
    ]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(color=colors, line=dict(color=borders, width=1.5)),
            text=[f"{v:.2f} min" for v in values],
            textposition="outside",
            textfont=dict(color="#0f172a", size=11, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
            width=0.5,
        )
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_LINE,
        margin=dict(l=10, r=20, t=30, b=30),
    )

    fig.update_layout(
        xaxis=dict(
            title="",
            showgrid=False,
            tickfont=dict(color="#334155", size=12, family="Inter"),
        ),
        yaxis=dict(
            title="",
            ticksuffix=" min",
            showgrid=True,
            gridcolor="#f1f5f9",
            rangemode="tozero",
        ),
        bargap=0.4,
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig