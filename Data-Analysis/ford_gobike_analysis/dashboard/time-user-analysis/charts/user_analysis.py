"""
charts/user_analysis.py – User Behavior & Demographic Visualizations
=====================================================================
Professional BI-grade redesign of the six User Analysis charts:

  1. User Type Distribution       – horizontal bars with dominant highlight
  2. Hourly Usage Pattern         – normalized multi-series temporal profile
  3. Average Duration by User Type – clean horizontal comparison + reference
  4. Trip Distribution by Age Group – chronologically ordered distribution
  5. Gender Distribution          – clean comparison bars with dominance
  6. User Type × Age Group        – 100% stacked composition with deltas

Column mapping (CSV → internal):
  - "user_type"      → used directly
  - "member_gender"  → used directly
  - "member_age"     → age_group derived internally (18-25, 26-35, 36-50, 51-65, 66-80)
  - "duration_min"   → used directly
  - "hour"           → used directly

Design principles:
  - Analytical readability first; consistent typography, spacing, hover language.
  - All percentages / dominance / peaks computed dynamically.
  - No legends for single-series charts; legends only when they add meaning.
  - Empty data returns empty_figure() with an actionable message.
  - All function names and signatures unchanged (used by dashboard_callbacks).
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_BAR, CHART_HEIGHT_LINE
from utils.theme import apply_chart_theme, empty_figure


# ---------------------------------------------------------------------------
# Shared design tokens
# ---------------------------------------------------------------------------
_AGE_GROUP_ORDER = ["18-25", "26-35", "36-50", "51-65", "66-80"]
_AGE_BINS = [18, 26, 36, 51, 66, 81]

# Primary palette (dashboard-consistent)
_TEAL        = COLORS["accent_teal"]
_TEAL_DARK   = "#0F766E"
_PURPLE      = COLORS["accent_purple"]
_PURPLE_DARK = "#7E22CE"
_AMBER       = "#F59E0B"
_AMBER_DARK  = "#B45309"
_SLATE       = "#64748B"
_SLATE_SOFT  = "#94A3B8"

# User-type palette (Subscriber = primary/dominant, Customer = secondary)
_USER_TYPE_COLORS = {
    "Subscriber": _TEAL,
    "Customer":   _PURPLE,
}
_USER_TYPE_BORDERS = {
    "Subscriber": _TEAL_DARK,
    "Customer":   _PURPLE_DARK,
}

# Gender palette (neutral, not stereotypical — uses dashboard accents)
_GENDER_COLORS = {
    "Male":   _TEAL,
    "Female": _PURPLE,
    "Other":  _AMBER,
}
_GENDER_BORDERS = {
    "Male":   _TEAL_DARK,
    "Female": _PURPLE_DARK,
    "Other":  _AMBER_DARK,
}

# Hover card (consistent across all charts)
_HOVER_LABEL = dict(
    bgcolor="rgba(15, 23, 42, 0.96)",
    bordercolor="rgba(255, 255, 255, 0.18)",
    font=dict(color="#ffffff", size=12, family="Inter"),
)

# Shared axis / grid styling
_GRID_COLOR = "#EEF2F6"
_AXIS_TEXT  = "#475569"
_AXIS_TITLE = "#334155"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _derive_age_group(member_age: pd.Series) -> pd.Series:
    """
    Convert a numeric `member_age` series into the canonical 5-bin age
    grouping used across the dashboard. Invalid / missing ages become NaN.
    """
    numeric_age = pd.to_numeric(member_age, errors="coerce")
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
    return empty_figure(message, height=height)


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _clean_gender_label(raw: str) -> str:
    """Normalize gender labels for display (title-cased, tidy)."""
    s = str(raw).strip()
    if not s:
        return "Unknown"
    return s.title()


# ---------------------------------------------------------------------------
# 1. User Type Distribution — horizontal bars, dynamic dominant highlight
# ---------------------------------------------------------------------------

def create_user_type_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    User type distribution as horizontal bars, sorted by trips (descending).

    Visual language:
      - Modern Donut Chart (hole=0.62) provides rich visual diversity.
      - Subscribers styled in primary brand Teal (#0d9488).
      - Customers styled in complementary Purple (#a855f7).
      - Center callout prominently displaying dominant percentage and role.
      - Sleek horizontal legend at the bottom with counts and shares.
    """
    if df.empty or "user_type" not in df.columns:
        return _empty("No user-type data available for the selected filters.", height=CHART_HEIGHT_BAR)

    counts = (
        df["user_type"]
        .dropna()
        .astype(str)
        .value_counts()
    )

    if counts.empty:
        return _empty("No user-type records in the selected filter scope.", height=CHART_HEIGHT_BAR)

    ordered_keys = [k for k in ["Subscriber", "Customer"] if k in counts.index]
    for k in counts.index:
        if k not in ordered_keys:
            ordered_keys.append(k)

    labels = ordered_keys
    values = [int(counts[k]) for k in labels]
    total = sum(values)

    color_map = {
        "Subscriber": _TEAL,
        "Customer": _PURPLE,
    }
    colors = [color_map.get(k, _SLATE) for k in labels]
    sub_pct = (counts.get("Subscriber", 0) / total * 100) if total else 0.0

    hover_texts = [
        f"<b>{k}</b><br>Trips: <b>{v:,}</b><br>Share of total: <b>{v/total*100:.1f}%</b>"
        for k, v in zip(labels, values)
    ]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(
                colors=colors,
                line=dict(color="#FFFFFF", width=2.5),
            ),
            textinfo="percent+label",
            texttemplate="<b>%{percent}</b><br>%{label}",
            textposition="inside",
            textfont=dict(color="#FFFFFF", size=11, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
            direction="clockwise",
            sort=False,
        )
    )

    # Center callout inside donut hole shows fleet total so no percentage is repeated
    fig.add_annotation(
        text=f"<b>{total:,}</b><br><span style='font-size:10px;font-weight:600;color:#64748B;'>TOTAL RIDES</span>",
        x=0.5,
        y=0.5,
        font=dict(size=16, family="Inter", color="#0F172A"),
        showarrow=False,
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_BAR,
        margin=dict(l=14, r=14, t=14, b=30),
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.04,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter", size=11, color=_AXIS_TEXT),
        ),
        hoverlabel=_HOVER_LABEL,
    )

    return fig


# ---------------------------------------------------------------------------
# 2. Hourly Usage Pattern by User Type — normalized multi-series profile
# ---------------------------------------------------------------------------

def create_user_type_hour_chart(df: pd.DataFrame) -> go.Figure:
    """
    Hourly usage pattern per user type (normalized within each user type).

    Each curve sums to 100% of that user type's trips, so the two curves
    are directly comparable regardless of absolute volume. Peak hour per
    series is annotated dynamically.
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

    matrix = (
        working.assign(user_type=working["user_type"].astype(str))
               .groupby(["hour", "user_type"])
               .size()
               .unstack(fill_value=0)
               .reindex(index=range(24), fill_value=0)
    )

    totals = matrix.sum(axis=0)
    normalized = matrix.div(totals.replace(0, pd.NA), axis=1) * 100
    normalized = normalized.fillna(0)

    if normalized.values.sum() == 0:
        return _empty(
            "No hourly user-type records in the selected filter scope.",
            height=CHART_HEIGHT_LINE,
        )

    hours = list(range(24))
    fig = go.Figure()

    for user_type in normalized.columns:
        y_vals = normalized[user_type].values.astype(float)
        color = _USER_TYPE_COLORS.get(user_type, _SLATE_SOFT)
        border = _USER_TYPE_BORDERS.get(user_type, _SLATE)

        peak_idx = int(y_vals.argmax())
        peak_hour = hours[peak_idx]
        peak_val  = float(y_vals[peak_idx])

        hover_texts = [
            f"<b>{user_type}</b><br>"
            f"{h:02d}:00 – {h:02d}:59<br>"
            f"Share of {user_type} trips: <b>{v:.2f}%</b>"
            for h, v in zip(hours, y_vals)
        ]

        # Gradient area beneath each curve for gentle emphasis
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=y_vals,
                mode="lines",
                line=dict(width=0, shape="spline", smoothing=0.6),
                fill="tozeroy",
                fillcolor=_hex_to_rgba(color, 0.10),
                hoverinfo="skip",
                showlegend=False,
            )
        )

        # Main line
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=y_vals,
                mode="lines+markers",
                name=user_type,
                line=dict(color=color, width=2.6, shape="spline", smoothing=0.6),
                marker=dict(
                    size=5,
                    color="#FFFFFF",
                    line=dict(color=color, width=1.6),
                ),
                hovertext=hover_texts,
                hoverinfo="text",
            )
        )

        # Dynamic peak marker + callout
        fig.add_trace(
            go.Scatter(
                x=[peak_hour],
                y=[peak_val],
                mode="markers",
                marker=dict(
                    size=14,
                    color=color,
                    line=dict(color="#FFFFFF", width=2),
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_annotation(
            x=peak_hour,
            y=peak_val,
            text=(
                f"<b>{user_type} peak</b><br>"
                f"{peak_hour:02d}:00 · "
                f"<span style='color:{border};font-weight:700;'>{peak_val:.2f}%</span>"
            ),
            showarrow=True,
            arrowhead=0,
            arrowcolor=color,
            arrowwidth=1.1,
            ax=0,
            ay=-34,
            bgcolor="rgba(255,255,255,0.98)",
            bordercolor=color,
            borderwidth=1,
            borderpad=4,
            font=dict(color="#0F172A", size=10, family="Inter"),
            align="center",
        )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_LINE,
        margin=dict(l=14, r=30, t=42, b=42),
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            font=dict(size=11, color=_AXIS_TEXT, family="Inter"),
            bgcolor="rgba(255,255,255,0.0)",
        ),
        xaxis=dict(
            title=dict(text="Hour of Day", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            tickmode="array",
            tickvals=list(range(0, 24, 2)),
            ticktext=[f"{h:02d}" for h in range(0, 24, 2)],
            showgrid=False,
            zeroline=False,
            range=[-0.7, 23.7],
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        yaxis=dict(
            title=dict(text="Share of User Type Trips (%)", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            ticksuffix="%",
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            rangemode="tozero",
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        hoverlabel=_HOVER_LABEL,
    )

    return fig


# ---------------------------------------------------------------------------
# 3. Average Trip Duration by User Type — horizontal bars + reference
# ---------------------------------------------------------------------------

def create_avg_duration_by_user_type_chart(df: pd.DataFrame) -> go.Figure:
    """
    Horizontal comparison of average trip duration between user types.

    The overall mean duration is computed from actual trip-level records
    (not the mean of the per-category means) and shown as a reference line.
    """
    if df.empty or "user_type" not in df.columns or "duration_min" not in df.columns:
        return _empty("No duration data available for the selected filters.")

    working = df[["user_type", "duration_min"]].dropna()
    if working.empty:
        return _empty("No duration records in the selected filter scope.")

    working = working.assign(user_type=working["user_type"].astype(str))

    grouped = (
        working.groupby("user_type")["duration_min"]
               .agg(avg_duration="mean", trip_count="count")
    )

    if grouped.empty:
        return _empty("No duration records in the selected filter scope.")

    # Overall mean from trip-level records (correct denominator)
    overall_mean = float(working["duration_min"].mean())

    # Sort ascending so the largest category sits on top
    grouped = grouped.sort_values("avg_duration", ascending=True)

    labels = grouped.index.tolist()
    avgs   = grouped["avg_duration"].tolist()
    counts = grouped["trip_count"].tolist()

    colors, borders = [], []
    for lbl in labels:
        base = _USER_TYPE_COLORS.get(lbl, _SLATE_SOFT)
        border = _USER_TYPE_BORDERS.get(lbl, _SLATE)
        colors.append(base)
        borders.append(border)

    bar_text = [f"<b>{v:.1f} min</b>" for v in avgs]

    hover_texts = [
        f"<b>{lbl}</b><br>"
        f"Average duration: <b>{v:.2f} min</b><br>"
        f"Trips analysed: <b>{int(c):,}</b>"
        for lbl, v, c in zip(labels, avgs, counts)
    ]

    fig = go.Figure(
        go.Bar(
            x=avgs,
            y=labels,
            orientation="h",
            marker=dict(color=colors, line=dict(color=borders, width=1.4)),
            text=bar_text,
            textposition="outside",
            textfont=dict(color="#0F172A", size=12, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
            cliponaxis=False,
            showlegend=False,
        )
    )

    # Reference line at the overall mean (from trip-level data)
    fig.add_vline(
        x=overall_mean,
        line=dict(color=_SLATE, width=1, dash="dot"),
        annotation_text=f"Overall mean · {overall_mean:.1f} min",
        annotation_position="top",
        annotation_font=dict(color=_SLATE, size=10, family="Inter"),
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_BAR,
        margin=dict(l=10, r=90, t=44, b=34),
    )

    fig.update_layout(
        xaxis=dict(
            title=dict(text="Average Duration (minutes)", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            rangemode="tozero",
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color=_AXIS_TEXT, size=12, family="Inter"),
        ),
        bargap=0.45,
        hoverlabel=_HOVER_LABEL,
        showlegend=False,
    )

    return fig


# ---------------------------------------------------------------------------
# 4. Trip Distribution by Age Group — chronological, dominant highlight
# ---------------------------------------------------------------------------

def create_age_group_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Trip distribution across age groups in chronological order.

    The dominant age group receives the primary accent; the rest are muted
    so the distribution's center of gravity is immediately visible.
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
    dominant_label = counts.idxmax()
    dominant_val = int(counts.max())
    dominant_share = (dominant_val / total * 100.0) if total else 0.0

    colors, borders = [], []
    for lbl in labels:
        if lbl == dominant_label:
            colors.append(_TEAL)
            borders.append(_TEAL_DARK)
        else:
            colors.append(_hex_to_rgba(_TEAL, 0.55))
            borders.append(_hex_to_rgba(_TEAL_DARK, 0.55))

    bar_text = [
        f"<b>{v / 1000:.1f}K</b> ({v / total * 100:.1f}%)" if v >= 1000 else f"<b>{v}</b>"
        for v in values
    ]

    hover_texts = [
        f"<b>{lbl} years</b><br>"
        f"Trips: <b>{v:,}</b><br>"
        f"Share of total: <b>{v / total * 100:.1f}%</b>"
        for lbl, v in zip(labels, values)
    ]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(color=colors, line=dict(color=borders, width=1.4)),
            text=bar_text,
            textposition="outside",
            textfont=dict(color="#0F172A", size=11, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
            cliponaxis=False,
            showlegend=False,
        )
    )

    # Dynamic peak annotation pointing to the largest cohort bar
    fig.add_annotation(
        x=dominant_label,
        y=dominant_val,
        text=f"▲ Peak: {dominant_label} ({dominant_share:.1f}%)",
        showarrow=True,
        arrowhead=2,
        arrowsize=0.8,
        arrowwidth=1.5,
        arrowcolor=_TEAL_DARK,
        ax=0,
        ay=-32,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=_TEAL,
        borderwidth=1,
        borderpad=4,
        font=dict(color="#0F172A", size=10, family="Inter"),
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_BAR,
        margin=dict(l=14, r=14, t=44, b=34),
    )

    max_val = max(values) if values else 100
    fig.update_layout(
        xaxis=dict(
            title=dict(text="Age Group (years)", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            showgrid=False,
            zeroline=False,
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        yaxis=dict(
            title=dict(text="Trip Volume", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            tickformat=",",
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            range=[0, max_val * 1.20],
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        bargap=0.35,
        hoverlabel=_HOVER_LABEL,
        showlegend=False,
    )

    return fig


# ---------------------------------------------------------------------------
# 5. Gender Distribution — horizontal comparison with dominance highlight
# ---------------------------------------------------------------------------

def create_gender_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Distribution of trips across gender categories, sorted by trips.

    Neutral, non-stereotypical palette. Dominant category receives the
    primary accent for immediate visual hierarchy.
    """
    if df.empty or "member_gender" not in df.columns:
        return _empty("No gender data available for the selected filters.")

    cleaned = (
        df["member_gender"]
        .dropna()
        .astype(str)
        .map(_clean_gender_label)
    )

    if cleaned.empty:
        return _empty("No gender records in the selected filter scope.")

    counts = cleaned.value_counts()

    if counts.empty:
        return _empty("No gender records in the selected filter scope.")

    counts = counts.sort_values(ascending=True)
    labels = counts.index.tolist()
    values = counts.values.astype(int)
    total  = int(values.sum())
    dominant_label = counts.idxmax()
    dominant_share = (counts.max() / total * 100.0) if total else 0.0

    colors, borders = [], []
    for lbl in labels:
        base = _GENDER_COLORS.get(lbl, _SLATE_SOFT)
        border = _GENDER_BORDERS.get(lbl, _SLATE)
        if lbl == dominant_label:
            colors.append(base)
            borders.append(border)
        else:
            colors.append(_hex_to_rgba(base, 0.55))
            borders.append(_hex_to_rgba(border, 0.55))

    bar_text = [
        f"<b>{v:,}</b>  ({v / total * 100:.1f}%)"
        for v in values
    ]

    hover_texts = [
        f"<b>{lbl}</b><br>"
        f"Trips: <b>{v:,}</b><br>"
        f"Share of total: <b>{v / total * 100:.1f}%</b>"
        for lbl, v in zip(labels, values)
    ]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=colors, line=dict(color=borders, width=1.4)),
            text=bar_text,
            textposition="outside",
            textfont=dict(color="#0F172A", size=12, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
            cliponaxis=False,
            showlegend=False,
        )
    )

    # Dominant callout
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.0,
        y=1.14,
        xanchor="left",
        yanchor="bottom",
        text=(
            f"<span style='color:#0F172A;font-weight:700;font-size:12px;'>"
            f"{dominant_label}</span> "
            f"<span style='color:{_SLATE};font-size:11px;'>riders represent</span> "
            f"<span style='color:{_TEAL_DARK};font-weight:700;font-size:12px;'>"
            f"{dominant_share:.1f}%</span> "
            f"<span style='color:{_SLATE};font-size:11px;'>of trips</span>"
        ),
        showarrow=False,
        align="left",
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_BAR,
        margin=dict(l=10, r=90, t=42, b=30),
    )

    fig.update_layout(
        xaxis=dict(
            title=dict(text="Number of Trips", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            tickformat=",",
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            rangemode="tozero",
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color=_AXIS_TEXT, size=12, family="Inter"),
        ),
        bargap=0.5,
        hoverlabel=_HOVER_LABEL,
        showlegend=False,
    )

    return fig


# ---------------------------------------------------------------------------
# 6. User Type Distribution Across Age Groups — 100% stacked composition
# ---------------------------------------------------------------------------

def create_user_type_by_age_group_chart(df: pd.DataFrame) -> go.Figure:
    """
    100% stacked composition of user types inside each age group.

    Each bar sums to 100%, so the Subscriber/Customer ratio is directly
    comparable across age groups regardless of cohort size. In-segment
    labels appear only when the segment is large enough to read.
    """
    if df.empty or "member_age" not in df.columns or "user_type" not in df.columns:
        return _empty("No age or user-type data available for the selected filters.")

    working = df[["member_age", "user_type"]].copy()
    working["age_group"] = _derive_age_group(working["member_age"])
    working = working.dropna(subset=["age_group", "user_type"])

    if working.empty:
        return _empty("No valid age & user-type records in the selected filter scope.")

    working["user_type"] = working["user_type"].astype(str)

    matrix = (
        working.groupby(["age_group", "user_type"])
               .size()
               .unstack(fill_value=0)
               .reindex(_AGE_GROUP_ORDER, fill_value=0)
    )

    for ut in _USER_TYPE_COLORS.keys():
        if ut not in matrix.columns:
            matrix[ut] = 0

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
        border = _USER_TYPE_BORDERS[user_type]

        hover_texts = [
            f"<b>{ag} years</b><br>"
            f"{user_type}: <b>{pct:.1f}%</b><br>"
            f"({int(cnt):,} of {int(tot):,} trips)"
            for ag, pct, cnt, tot in zip(age_groups, pct_vals, raw_counts, row_totals_vals)
        ]

        # In-segment text only when wide enough (>=8%) to avoid clutter
        text_vals = [
            f"<b>{p:.1f}%</b>" if p >= 8 else ""
            for p in pct_vals
        ]

        fig.add_trace(
            go.Bar(
                x=age_groups,
                y=pct_vals,
                name=user_type,
                marker=dict(color=color, line=dict(color=border, width=1.0)),
                hovertext=hover_texts,
                hoverinfo="text",
                text=text_vals,
                textposition="inside",
                textfont=dict(color="#FFFFFF", size=11, family="Inter"),
            )
        )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_BAR,
        margin=dict(l=10, r=20, t=42, b=42),
    )

    fig.update_layout(
        barmode="stack",
        bargap=0.35,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            font=dict(size=11, color=_AXIS_TEXT, family="Inter"),
        ),
        xaxis=dict(
            title=dict(text="Age Group (years)", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            showgrid=False,
            zeroline=False,
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        yaxis=dict(
            title=dict(text="Composition within Age Group (%)", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            ticksuffix="%",
            range=[0, 100],
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        hoverlabel=_HOVER_LABEL,
    )

    return fig