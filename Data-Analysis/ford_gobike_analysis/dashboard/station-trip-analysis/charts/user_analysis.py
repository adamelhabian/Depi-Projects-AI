"""
charts/user_analysis.py – User Behavior & Demographic Visualizations
=====================================================================
Plotly chart generators styled with the Tailwind aesthetic used across
the other chart modules (station_analysis.py / trip_analysis.py /
time_analysis.py):

  1. User Type Distribution (donut / pie)
  2. Hourly Usage Pattern by User Type (normalized multi-line)
  3. Average Trip Duration by User Type (bar comparison)
  4. Trip Distribution by Age Group (bar)
  5. Gender Distribution (donut / pie)
  6. User Type Distribution Across Age Groups (100% stacked bar)

Column mapping (CSV → internal):
  - "user_type"      → used directly
  - "member_gender"  → used directly
  - "member_age"     → age_group derived internally (18-25, 26-35, 36-50, 51-65, 66-80)
  - "duration_min"   → used directly
  - "hour"           → used directly

Design notes:
  - All functions return go.Figure.
  - Empty inputs return empty_figure() with a context-appropriate message.
  - Missing / invalid values are handled safely (no crash on NaN).
  - Dark hoverlabel card matching the rest of the dashboard.
  - No external preprocessing needed — everything self-contained.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_BAR, CHART_HEIGHT_LINE
from utils.theme import apply_chart_theme, empty_figure


# Canonical age group ordering (matches EDA notebook)
_AGE_GROUP_ORDER = ["18-25", "26-35", "36-50", "51-65", "66-80"]

# Age group boundaries (inclusive lower, exclusive upper)
_AGE_BINS = [18, 26, 36, 51, 66, 81]

# Palette used for user-type comparisons (Subscriber vs Customer)
_USER_TYPE_COLORS = {
    "Subscriber": "#0d9488",   # teal
    "Customer":   "#a855f7",   # purple
}

# Palette for gender categories
_GENDER_COLORS = {
    "Male":   "#0d9488",
    "Female": "#a855f7",
    "Other":  "#f59e0b",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _derive_age_group(member_age: pd.Series) -> pd.Series:
    """
    Convert a numeric `member_age` series into the canonical 6-bin age
    grouping used across the dashboard.

    Returns a Series of categorical strings; invalid / missing ages become NaN.
    """
    numeric_age = pd.to_numeric(member_age, errors="coerce")
    # Accept only realistic adult ages; ignore sentinel values (e.g., birth year 1900)
    numeric_age = numeric_age.where((numeric_age >= 18) & (numeric_age <= 80))

    binned = pd.cut(
        numeric_age,
        bins=_AGE_BINS,
        labels=_AGE_GROUP_ORDER,
        right=False,
        include_lowest=True,
    )
    return binned


def _empty(message: str, height: int = CHART_HEIGHT_BAR) -> go.Figure:
    """Small wrapper to keep empty_figure calls terse and consistent."""
    return empty_figure(message, height=height)


# ---------------------------------------------------------------------------
# 1. User Type Distribution
# ---------------------------------------------------------------------------

def create_user_type_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Donut chart showing the share of trips by user_type
    (Subscriber vs Customer).
    """
    if df.empty or "user_type" not in df.columns:
        return _empty("No user-type data available for the selected filters.")

    counts = (
        df["user_type"]
        .dropna()
        .astype(str)
        .value_counts()
    )

    if counts.empty:
        return _empty("No user-type records in the selected filter scope.")

    labels = counts.index.tolist()
    values = counts.values.tolist()
    total = int(sum(values))

    colors = [_USER_TYPE_COLORS.get(lbl, "#94a3b8") for lbl in labels]

    hover_texts = [
        f"<b>{lbl}</b><br>"
        f"Trips: <b>{int(v):,}</b> ({v / total * 100:.1f}%)"
        for lbl, v in zip(labels, values)
    ]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(
                colors=colors,
                line=dict(color="#ffffff", width=2),
            ),
            textinfo="label+percent",
            textfont=dict(color="#0f172a", size=11, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
            sort=False,
            direction="clockwise",
        )
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_BAR,
        margin=dict(l=10, r=10, t=10, b=10),
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#334155", family="Inter"),
        ),
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# 2. Hourly Usage Pattern by User Type
# ---------------------------------------------------------------------------

def create_user_type_hour_chart(df: pd.DataFrame) -> go.Figure:
    """
    Line chart of hourly usage normalized within each user type.

    Each user type's hourly distribution sums to 100%, so the two curves
    can be compared on the same scale regardless of their absolute volume.
    """
    if df.empty or "hour" not in df.columns or "user_type" not in df.columns:
        return _empty(
            "No hourly user-type data available for the selected filters.",
            height=CHART_HEIGHT_LINE,
        )

    working = df[["hour", "user_type"]].dropna()
    if working.empty:
        return _empty(
            "No hourly user-type records in the selected filter scope.",
            height=CHART_HEIGHT_LINE,
        )

    # Cross-tab: rows = hour, columns = user_type, values = counts
    matrix = (
        working.assign(user_type=working["user_type"].astype(str))
               .groupby(["hour", "user_type"])
               .size()
               .unstack(fill_value=0)
               .reindex(index=range(24), fill_value=0)
    )

    # Normalize each user_type column to % of that user type's total trips
    totals = matrix.sum(axis=0)
    # Avoid division by zero
    normalized = matrix.div(totals.replace(0, pd.NA), axis=1) * 100
    normalized = normalized.fillna(0)

    if normalized.values.sum() == 0:
        return _empty(
            "No hourly user-type records in the selected filter scope.",
            height=CHART_HEIGHT_LINE,
        )

    fig = go.Figure()

    for user_type in normalized.columns:
        y_vals = normalized[user_type].values
        color = _USER_TYPE_COLORS.get(user_type, "#94a3b8")

        hover_texts = [
            f"<b>{user_type}</b><br>"
            f"{h:02d}:00 – {h:02d}:59<br>"
            f"Share: <b>{v:.2f}%</b> of {user_type} trips"
            for h, v in enumerate(y_vals)
        ]

        fig.add_trace(
            go.Scatter(
                x=list(range(24)),
                y=y_vals,
                mode="lines+markers",
                name=user_type,
                line=dict(color=color, width=2.5, shape="spline"),
                marker=dict(
                    size=6,
                    color=color,
                    line=dict(color="#ffffff", width=1.2),
                ),
                hovertext=hover_texts,
                hoverinfo="text",
            )
        )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_LINE,
        margin=dict(l=10, r=20, t=10, b=30),
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#334155", family="Inter"),
        ),
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
            ticksuffix="%",
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
# 3. Average Trip Duration by User Type
# ---------------------------------------------------------------------------

def create_avg_duration_by_user_type_chart(df: pd.DataFrame) -> go.Figure:
    """
    Bar chart comparing average trip duration (minutes) between user types.
    """
    if df.empty or "user_type" not in df.columns or "duration_min" not in df.columns:
        return _empty("No duration data available for the selected filters.")

    working = df[["user_type", "duration_min"]].dropna()
    if working.empty:
        return _empty("No duration records in the selected filter scope.")

    grouped = (
        working.assign(user_type=working["user_type"].astype(str))
               .groupby("user_type")["duration_min"]
               .mean()
               .sort_values(ascending=False)
    )

    if grouped.empty:
        return _empty("No duration records in the selected filter scope.")

    labels = grouped.index.tolist()
    values = [float(v) for v in grouped.values]
    colors = [_USER_TYPE_COLORS.get(lbl, "#94a3b8") for lbl in labels]
    borders = ["#0f766e" if c == "#0d9488" else "#9333ea" if c == "#a855f7" else "#64748b"
               for c in colors]

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
        height=CHART_HEIGHT_BAR,
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


# ---------------------------------------------------------------------------
# 4. Trip Distribution by Age Group
# ---------------------------------------------------------------------------

def create_age_group_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Bar chart showing the distribution of trips across age groups.
    Age groups are derived internally from `member_age`.
    """
    if df.empty or "member_age" not in df.columns:
        return _empty("No age data available for the selected filters.")

    age_groups = _derive_age_group(df["member_age"]).dropna()
    if age_groups.empty:
        return _empty("No valid age records in the selected filter scope.")

    counts = age_groups.value_counts().reindex(_AGE_GROUP_ORDER, fill_value=0)
    if counts.sum() == 0:
        return _empty("No valid age records in the selected filter scope.")

    labels = counts.index.tolist()
    values = [int(v) for v in counts.values]
    total = int(sum(values))

    # Rank-opacity teal gradient
    n_bars = len(labels)
    colors = [
        f"rgba(13, 148, 136, {1.0 - (i / max(1, n_bars - 1)) * 0.55:.2f})"
        for i in range(n_bars)
    ]

    hover_texts = [
        f"<b>{lbl}</b><br>"
        f"Trips: <b>{v:,}</b> ({v / total * 100:.1f}%)"
        for lbl, v in zip(labels, values)
    ]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(color=colors, line=dict(color="#0f766e", width=1)),
            text=[f"{v:,}" for v in values],
            textposition="outside",
            textfont=dict(color="#0f172a", size=11, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
            width=0.6,
        )
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_BAR,
        margin=dict(l=10, r=20, t=30, b=30),
    )

    fig.update_layout(
        xaxis=dict(
            title="",
            showgrid=False,
            tickfont=dict(color="#334155", size=11, family="Inter"),
        ),
        yaxis=dict(
            title="",
            tickformat=",",
            showgrid=True,
            gridcolor="#f1f5f9",
            rangemode="tozero",
        ),
        bargap=0.35,
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# 5. Gender Distribution
# ---------------------------------------------------------------------------

def create_gender_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Donut chart showing the distribution of trips by member_gender.
    """
    if df.empty or "member_gender" not in df.columns:
        return _empty("No gender data available for the selected filters.")

    counts = (
        df["member_gender"]
        .dropna()
        .astype(str)
        .value_counts()
    )

    if counts.empty:
        return _empty("No gender records in the selected filter scope.")

    labels = counts.index.tolist()
    values = counts.values.tolist()
    total = int(sum(values))

    colors = [_GENDER_COLORS.get(lbl, "#94a3b8") for lbl in labels]

    hover_texts = [
        f"<b>{lbl}</b><br>"
        f"Trips: <b>{int(v):,}</b> ({v / total * 100:.1f}%)"
        for lbl, v in zip(labels, values)
    ]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(
                colors=colors,
                line=dict(color="#ffffff", width=2),
            ),
            textinfo="label+percent",
            textfont=dict(color="#0f172a", size=11, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
            sort=False,
            direction="clockwise",
        )
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_BAR,
        margin=dict(l=10, r=10, t=10, b=10),
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#334155", family="Inter"),
        ),
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# 6. User Type Distribution Across Age Groups (100% Stacked Bar)
# ---------------------------------------------------------------------------

def create_user_type_by_age_group_chart(df: pd.DataFrame) -> go.Figure:
    """
    Stacked bar chart showing user_type composition inside each age group.

    Each bar sums to 100%, so the ratio of Subscribers vs Customers within
    every age group is directly comparable regardless of group size.
    """
    if df.empty or "member_age" not in df.columns or "user_type" not in df.columns:
        return _empty("No age or user-type data available for the selected filters.")

    working = df[["member_age", "user_type"]].copy()
    working["age_group"] = _derive_age_group(working["member_age"])
    working = working.dropna(subset=["age_group", "user_type"])

    if working.empty:
        return _empty("No valid age & user-type records in the selected filter scope.")

    working["user_type"] = working["user_type"].astype(str)

    # Cross-tab: rows = age group, columns = user_type, values = counts
    matrix = (
        working.groupby(["age_group", "user_type"])
               .size()
               .unstack(fill_value=0)
               .reindex(_AGE_GROUP_ORDER, fill_value=0)
    )

    # Ensure both user types are present as columns even if one is missing
    for ut in _USER_TYPE_COLORS.keys():
        if ut not in matrix.columns:
            matrix[ut] = 0

    # Normalize each row to 100%
    row_totals = matrix.sum(axis=1)
    normalized = matrix.div(row_totals.replace(0, pd.NA), axis=0) * 100
    normalized = normalized.fillna(0)

    if normalized.values.sum() == 0:
        return _empty("No valid age & user-type records in the selected filter scope.")

    age_groups = normalized.index.tolist()

    fig = go.Figure()

    for user_type in _USER_TYPE_COLORS.keys():
        if user_type not in normalized.columns:
            continue

        pct_vals = normalized[user_type].values
        raw_counts = matrix[user_type].values
        row_totals_vals = row_totals.values

        color = _USER_TYPE_COLORS[user_type]

        hover_texts = [
            f"<b>{ag}</b><br>"
            f"{user_type}: <b>{pct:.1f}%</b><br>"
            f"({int(cnt):,} of {int(tot):,} trips)"
            for ag, pct, cnt, tot in zip(age_groups, pct_vals, raw_counts, row_totals_vals)
        ]

        fig.add_trace(
            go.Bar(
                x=age_groups,
                y=pct_vals,
                name=user_type,
                marker=dict(
                    color=color,
                    line=dict(color="#ffffff", width=1),
                ),
                hovertext=hover_texts,
                hoverinfo="text",
                text=[f"{p:.1f}%" if p >= 5 else "" for p in pct_vals],
                textposition="inside",
                textfont=dict(color="#ffffff", size=10, family="Inter"),
            )
        )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_BAR,
        margin=dict(l=10, r=20, t=10, b=30),
    )

    fig.update_layout(
        barmode="stack",
        bargap=0.35,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#334155", family="Inter"),
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            tickfont=dict(color="#334155", size=11, family="Inter"),
        ),
        yaxis=dict(
            title="",
            ticksuffix="%",
            range=[0, 100],
            showgrid=True,
            gridcolor="#f1f5f9",
        ),
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            font=dict(color="#ffffff", size=11, family="Inter"),
        ),
    )

    return fig