"""
charts/time_analysis.py – Temporal Usage & Duration Visualizations
====================================================================
Professional BI-grade redesign of the four Time Analysis charts:

  1. Hourly Trip Demand        – smooth demand profile with gradient area
  2. Day-of-Week × Hour Matrix – demand-intensity heatmap with peak callout
  3. Hourly Duration Profile   – duration curve with min/max annotations
  4. Weekday vs Weekend        – comparison bars with delta callout

Column mapping (CSV → internal):
  - "hour"          → used for hourly analyses (T1, T3, and heatmap columns)
  - "day_of_week"   → used for the Day × Hour heatmap rows
  - "duration_min"  → used for both duration charts
  - weekend_flag    → derived internally from day_of_week

Design principles:
  - Analytical readability first; visual polish second.
  - All peaks / mins / deltas computed dynamically from data.
  - Consistent typography, spacing, hover language across all four charts.
  - No legends for single-series charts.
  - Empty data returns empty_figure() with an actionable message.
  - All function names and signatures unchanged (used by dashboard_callbacks).
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from config import COLORS, CHART_HEIGHT_LINE, CHART_HEIGHT_HEATMAP
from utils.theme import apply_chart_theme, empty_figure


# ---------------------------------------------------------------------------
# Shared design tokens (consistent across all four charts)
# ---------------------------------------------------------------------------
_DAY_ORDER = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",
]
_WEEKEND_DAYS = {"Saturday", "Sunday"}

# Hover card — consistent across charts
_HOVER_LABEL = dict(
    bgcolor="rgba(15, 23, 42, 0.96)",
    bordercolor="rgba(255, 255, 255, 0.18)",
    font=dict(color="#ffffff", size=12, family="Inter"),
)

# Grid tint for subtle reference lines
_GRID_COLOR = "#EEF2F6"
_AXIS_TEXT  = "#475569"
_AXIS_TITLE = "#334155"

# Primary palette (dashboard-consistent)
_TEAL        = COLORS["accent_teal"]
_TEAL_DARK   = "#0F766E"
_TEAL_SOFT   = "rgba(13, 148, 136, 0.14)"

_PURPLE      = COLORS["accent_purple"]
_PURPLE_DARK = "#7E22CE"
_PURPLE_SOFT = "rgba(168, 85, 247, 0.14)"

_SLATE       = "#64748B"
_SLATE_SOFT  = "#F8FAFC"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalize_day_names(series: pd.Series) -> pd.Series:
    """Normalize day_of_week to Title Case so it matches _DAY_ORDER."""
    return series.astype(str).str.strip().str.title()


def _hour_ticks(step: int = 2) -> tuple[list[int], list[str]]:
    """Return (tickvals, ticktext) for the hour axis: 00, 02, ..., 22."""
    vals = list(range(0, 24, step))
    return vals, [f"{h:02d}" for h in vals]


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert #RRGGBB to rgba(r,g,b,alpha) for gradient area fills."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _empty(message: str, height: int) -> go.Figure:
    return empty_figure(message, height=height)


# ---------------------------------------------------------------------------
# 1. Hourly Trip Demand
# ---------------------------------------------------------------------------

def create_trips_by_hour_chart(df: pd.DataFrame) -> go.Figure:
    """
    Hourly trip-demand profile.

    Visual language:
      - Soft gradient area beneath the line → emphasizes magnitude.
      - Smooth line + discrete markers → trend + precision.
      - Vertical dashed reference at the peak hour + callout annotation.
      - Horizontal dashed reference at the average (baseline context).
    """
    if df.empty or "hour" not in df.columns:
        return _empty("No temporal data available for the selected filters.",
                      CHART_HEIGHT_LINE)

    trips_by_hour = (
        df.groupby("hour")
          .size()
          .reindex(range(24), fill_value=0)
    )

    if trips_by_hour.sum() == 0:
        return _empty("No trips recorded in the selected filter scope.",
                      CHART_HEIGHT_LINE)

    peak_hour = int(trips_by_hour.idxmax())
    peak_val  = int(trips_by_hour.max())
    avg_val   = float(trips_by_hour.mean())
    total_val = int(trips_by_hour.sum())

    # Peak cell's share of the day
    peak_share = (peak_val / total_val * 100.0) if total_val else 0.0

    hours = trips_by_hour.index.to_numpy()
    values = trips_by_hour.values.astype(float)

    hover_texts = [
        f"<b>{h:02d}:00 – {h:02d}:59</b><br>"
        f"Trips: <b>{int(v):,}</b><br>"
        f"Share of day: <b>{(v / total_val * 100 if total_val else 0):.1f}%</b>"
        + ("<br><span style='color:#5EEAD4;'>▲ Peak hour</span>" if h == peak_hour else "")
        for h, v in zip(hours, values)
    ]

    fig = go.Figure()

    # ── Gradient area under the curve ────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=values,
            mode="lines",
            line=dict(width=0, shape="spline", smoothing=0.85),
            fill="tozeroy",
            fillcolor=_hex_to_rgba(_TEAL, 0.16),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # ── Main line with markers ───────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=values,
            mode="lines+markers",
            line=dict(color=_TEAL, width=2.6, shape="spline", smoothing=0.85),
            marker=dict(
                size=6,
                color="#FFFFFF",
                line=dict(color=_TEAL, width=2),
            ),
            hovertext=hover_texts,
            hoverinfo="text",
            showlegend=False,
        )
    )

    # ── Peak marker (halo + solid core) ─────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=[peak_hour],
            y=[peak_val],
            mode="markers",
            marker=dict(
                size=22,
                color=_hex_to_rgba(_TEAL, 0.18),
                line=dict(color=_TEAL, width=0),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[peak_hour],
            y=[peak_val],
            mode="markers",
            marker=dict(
                size=11,
                color=_TEAL,
                line=dict(color="#FFFFFF", width=2),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # ── Average reference line ───────────────────────────────────────────
    fig.add_hline(
        y=avg_val,
        line=dict(color="#94A3B8", width=1, dash="dot"),
        annotation_text=f"Daily avg · {avg_val:,.0f}",
        annotation_position="right",
        annotation_font=dict(color="#64748B", size=10, family="Inter"),
    )

    # ── Peak annotation callout ──────────────────────────────────────────
    fig.add_annotation(
        x=peak_hour,
        y=peak_val,
        text=(
            f"<b>Peak · {peak_hour:02d}:00</b><br>"
            f"<span style='color:{_TEAL_DARK};font-weight:700;'>{peak_val:,} trips</span>"
            f" <span style='color:#64748B;'>({peak_share:.1f}%)</span>"
        ),
        showarrow=True,
        arrowhead=0,
        arrowcolor=_TEAL,
        arrowwidth=1.2,
        ax=0,
        ay=-38,
        bgcolor="rgba(255,255,255,0.98)",
        bordercolor=_TEAL,
        borderwidth=1,
        borderpad=5,
        font=dict(color="#0F172A", size=11, family="Inter"),
        align="center",
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_LINE,
        margin=dict(l=14, r=44, t=26, b=34),
    )

    tickvals, ticktext = _hour_ticks(2)
    fig.update_layout(
        xaxis=dict(
            title=dict(text="Hour of Day", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            showgrid=False,
            zeroline=False,
            range=[-0.7, 23.7],
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        yaxis=dict(
            title=dict(text="Trips", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            tickformat=",",
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            rangemode="tozero",
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
            ticksuffix="",
        ),
        hoverlabel=_HOVER_LABEL,
        showlegend=False,
    )

    return fig


# ---------------------------------------------------------------------------
# 2. Day-of-Week × Hour Demand Matrix
# ---------------------------------------------------------------------------

def create_day_hour_heatmap_chart(df: pd.DataFrame) -> go.Figure:
    """
    Demand-intensity matrix: day-of-week (rows) × hour (columns).

    Visual language:
      - Sequential single-hue color scale (cool slate → deep navy) with
        analytical meaning: light = low demand, dark = high demand.
      - Slightly larger gaps on row boundaries and a thin separator between
        weekdays and weekend for readability.
      - Dynamic peak-cell callout annotation.
      - Compact colorbar on the right with meaningful title.
    """
    if df.empty or "day_of_week" not in df.columns or "hour" not in df.columns:
        return _empty("No temporal data available for the selected filters.",
                      CHART_HEIGHT_HEATMAP)

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
        return _empty("No trips recorded in the selected filter scope.",
                      CHART_HEIGHT_HEATMAP)

    z = matrix.values.astype(float)
    vmax = float(z.max())
    vmin = 0.0

    # Locate peak cell (day index, hour index)
    peak_flat  = int(z.argmax())
    peak_day_i = peak_flat // z.shape[1]
    peak_hour  = int(peak_flat % z.shape[1])
    peak_day   = matrix.index[peak_day_i]
    peak_val   = int(z[peak_day_i, peak_hour])

    # Row totals → to label days with their share of week
    row_totals = z.sum(axis=1)
    week_total = row_totals.sum()

    # Peak-cell detection threshold for "Peak" vs "High" tags in hover
    high_cut = vmax * 0.75 if vmax > 0 else 0

    hover_texts = []
    for di, day in enumerate(matrix.index):
        row = []
        for h in range(24):
            v = int(z[di, h])
            if v == peak_val and di == peak_day_i and h == peak_hour:
                tag = "<span style='color:#FCA5A5;font-weight:700;'>▲ Peak</span>"
            elif v >= high_cut and v > 0:
                tag = "<span style='color:#FDE68A;'>● High</span>"
            else:
                tag = ""
            share = (v / week_total * 100.0) if week_total else 0.0
            row.append(
                f"<b>{day} · {h:02d}:00–{h:02d}:59</b><br>"
                f"Trips: <b>{v:,}</b><br>"
                f"Share of week: <b>{share:.2f}%</b>"
                + (f"<br>{tag}" if tag else "")
            )
        hover_texts.append(row)

    # Custom sequential colorscale (light → deep navy) with clear breakpoints
    colorscale = [
        [0.00, "#F8FAFC"],
        [0.10, "#E2E8F0"],
        [0.30, "#BFDBFE"],
        [0.55, "#60A5FA"],
        [0.75, "#2563EB"],
        [0.90, "#1E3A8A"],
        [1.00, "#0B1B3A"],
    ]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=list(range(24)),
            y=matrix.index.tolist(),
            colorscale=colorscale,
            zmin=vmin,
            zmax=vmax,
            hovertemplate="%{text}<extra></extra>",
            text=hover_texts,
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="Trips",
                    side="top",
                    font=dict(size=11, color=_AXIS_TITLE, family="Inter"),
                ),
                thickness=12,
                len=0.82,
                x=1.015,
                y=0.5,
                tickfont=dict(size=10, color="#64748B", family="Inter"),
                outlinewidth=0,
                ticks="outside",
                ticklen=3,
            ),
            xgap=2,
            ygap=2,
        )
    )

    # Peak cell outline overlay (white border + teal ring)
    fig.add_trace(
        go.Scatter(
            x=[peak_hour],
            y=[peak_day],
            mode="markers",
            marker=dict(
                symbol="square",
                size=34,
                color="rgba(0,0,0,0)",
                line=dict(color="#FFFFFF", width=2.5),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[peak_hour],
            y=[peak_day],
            mode="markers",
            marker=dict(
                symbol="square",
                size=40,
                color="rgba(0,0,0,0)",
                line=dict(color=_TEAL, width=1.6),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Peak callout annotation (placed above the matrix to avoid overlap)
    fig.add_annotation(
        x=peak_hour,
        y=peak_day,
        text=(
            f"<b>Network peak</b> · {peak_day} {peak_hour:02d}:00 "
            f"<span style='color:{_TEAL_DARK};font-weight:700;'>({peak_val:,})</span>"
        ),
        showarrow=True,
        arrowhead=0,
        arrowcolor=_TEAL,
        arrowwidth=1.2,
        ax=60,
        ay=-30,
        bgcolor="rgba(255,255,255,0.98)",
        bordercolor=_TEAL,
        borderwidth=1,
        borderpad=5,
        font=dict(color="#0F172A", size=11, family="Inter"),
        align="left",
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_HEATMAP,
        margin=dict(l=14, r=70, t=44, b=42),
    )

    tickvals, ticktext = _hour_ticks(2)

    fig.update_layout(
        xaxis=dict(
            title=dict(text="Hour of Day", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            showgrid=False,
            zeroline=False,
            side="bottom",
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
            ticks="outside",
            ticklen=3,
        ),
        yaxis=dict(
            title=dict(text="", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            showgrid=False,
            zeroline=False,
            autorange="reversed",
            tickfont=dict(color=_AXIS_TEXT, size=12, family="Inter"),
            ticks="",
        ),
        hoverlabel=_HOVER_LABEL,
        showlegend=False,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
    )

    return fig


# ---------------------------------------------------------------------------
# 3. Average Trip Duration by Hour
# ---------------------------------------------------------------------------

def create_avg_duration_by_hour_chart(df: pd.DataFrame) -> go.Figure:
    """
    Hourly duration profile.

    Visual language:
      - Purple gradient area beneath the curve (duration = purple family).
      - Peak and trough annotated directly (data-driven).
      - Horizontal reference at the overall average duration.
      - Y axis in minutes with a clean min suffix.
    """
    if df.empty or "hour" not in df.columns or "duration_min" not in df.columns:
        return _empty("No duration data available for the selected filters.",
                      CHART_HEIGHT_LINE)

    avg_dur = (
        df.groupby("hour")["duration_min"]
          .mean()
          .reindex(range(24))
    )
    plot_data = avg_dur.dropna()

    if plot_data.empty:
        return _empty("No duration data available for the selected filter scope.",
                      CHART_HEIGHT_LINE)

    peak_hour = int(plot_data.idxmax())
    peak_val  = float(plot_data.max())
    min_hour  = int(plot_data.idxmin())
    min_val   = float(plot_data.min())
    avg_val   = float(plot_data.mean())

    spread = peak_val - min_val

    hours  = plot_data.index.to_numpy()
    values = plot_data.values.astype(float)

    hover_texts = [
        f"<b>{h:02d}:00 – {h:02d}:59</b><br>"
        f"Average duration: <b>{v:.1f} min</b>"
        for h, v in zip(hours, values)
    ]

    fig = go.Figure()

    # ── Gradient area ────────────────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=values,
            mode="lines",
            line=dict(width=0, shape="spline", smoothing=0.85),
            fill="tozeroy",
            fillcolor=_hex_to_rgba(_PURPLE, 0.14),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # ── Main line ────────────────────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=values,
            mode="lines+markers",
            line=dict(color=_PURPLE, width=2.6, shape="spline", smoothing=0.85),
            marker=dict(
                size=6,
                color="#FFFFFF",
                line=dict(color=_PURPLE, width=2),
            ),
            hovertext=hover_texts,
            hoverinfo="text",
            showlegend=False,
        )
    )

    # ── Peak marker halo ─────────────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=[peak_hour],
            y=[peak_val],
            mode="markers",
            marker=dict(
                size=22,
                color=_hex_to_rgba(_PURPLE, 0.18),
                line=dict(color=_PURPLE, width=0),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[peak_hour],
            y=[peak_val],
            mode="markers",
            marker=dict(
                size=11,
                color=_PURPLE,
                line=dict(color="#FFFFFF", width=2),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # ── Average reference line ───────────────────────────────────────────
    fig.add_hline(
        y=avg_val,
        line=dict(color="#94A3B8", width=1, dash="dot"),
        annotation_text=f"Mean · {avg_val:.1f} min",
        annotation_position="right",
        annotation_font=dict(color="#64748B", size=10, family="Inter"),
    )

    # ── Peak callout ─────────────────────────────────────────────────────
    fig.add_annotation(
        x=peak_hour,
        y=peak_val,
        text=(
            f"<b>Longest rides · {peak_hour:02d}:00</b><br>"
            f"<span style='color:{_PURPLE_DARK};font-weight:700;'>{peak_val:.1f} min</span>"
        ),
        showarrow=True,
        arrowhead=0,
        arrowcolor=_PURPLE,
        arrowwidth=1.2,
        ax=0,
        ay=-38,
        bgcolor="rgba(255,255,255,0.98)",
        bordercolor=_PURPLE,
        borderwidth=1,
        borderpad=5,
        font=dict(color="#0F172A", size=11, family="Inter"),
        align="center",
    )

    # ── Minimum callout (placed below the line) ──────────────────────────
    fig.add_annotation(
        x=min_hour,
        y=min_val,
        text=(
            f"<b>Shortest rides · {min_hour:02d}:00</b><br>"
            f"<span style='color:{_PURPLE_DARK};font-weight:700;'>{min_val:.1f} min</span>"
        ),
        showarrow=True,
        arrowhead=0,
        arrowcolor="#94A3B8",
        arrowwidth=1.0,
        ax=0,
        ay=34,
        bgcolor="rgba(255,255,255,0.98)",
        bordercolor="#CBD5E1",
        borderwidth=1,
        borderpad=4,
        font=dict(color="#0F172A", size=10, family="Inter"),
        align="center",
    )

    # Peak-to-trough spread note in the top-left corner
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.01,
        y=1.12,
        text=(
            f"<span style='color:#64748B;font-size:11px;'>"
            f"Peak–trough spread across the day: "
            f"<b style='color:{_PURPLE_DARK};'>{spread:.1f} min</b></span>"
        ),
        showarrow=False,
        align="left",
    )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_LINE,
        margin=dict(l=14, r=54, t=40, b=42),
    )

    tickvals, ticktext = _hour_ticks(2)
    fig.update_layout(
        xaxis=dict(
            title=dict(text="Hour of Day", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            showgrid=False,
            zeroline=False,
            range=[-0.7, 23.7],
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        yaxis=dict(
            title=dict(text="Average Duration (minutes)", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            rangemode="tozero",
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        hoverlabel=_HOVER_LABEL,
        showlegend=False,
    )

    return fig


# ---------------------------------------------------------------------------
# 4. Weekday vs Weekend Average Duration
# ---------------------------------------------------------------------------

def create_weekday_vs_weekend_duration_chart(df: pd.DataFrame) -> go.Figure:
    """
    Weekday vs weekend average duration comparison.

    Visual language:
      - Two prominent bars with value labels above them.
      - A dynamic delta callout describing the difference (data-driven).
      - Optional percentage delta shown only when meaningful (>0.1%).
      - Baseline reference at the overall mean for context.
    """
    if df.empty or "day_of_week" not in df.columns or "duration_min" not in df.columns:
        return _empty("No duration data available for the selected filters.",
                      CHART_HEIGHT_LINE)

    df_local = df.copy()
    df_local["_day_norm"] = _normalize_day_names(df_local["day_of_week"])
    df_local["_is_weekend"] = df_local["_day_norm"].isin(_WEEKEND_DAYS)

    # Compute both means and both counts
    wd = df_local.loc[~df_local["_is_weekend"], "duration_min"]
    we = df_local.loc[ df_local["_is_weekend"], "duration_min"]

    weekday_val = float(wd.mean()) if not wd.empty else 0.0
    weekend_val = float(we.mean()) if not we.empty else 0.0

    if weekday_val == 0.0 and weekend_val == 0.0:
        return _empty("No duration data available for the selected filter scope.",
                      CHART_HEIGHT_LINE)

    overall_mean = (
        (weekday_val * len(wd) + weekend_val * len(we)) / (len(wd) + len(we))
        if (len(wd) + len(we)) else 0.0
    )

    labels = ["Weekday", "Weekend"]
    values = [weekday_val, weekend_val]
    counts = [int(len(wd)), int(len(we))]
    colors = [_TEAL, _PURPLE]
    borders = [_TEAL_DARK, _PURPLE_DARK]

    hover_texts = [
        f"<b>{lbl}</b><br>"
        f"Average duration: <b>{v:.2f} min</b><br>"
        f"Trips analysed: <b>{c:,}</b>"
        for lbl, v, c in zip(labels, values, counts)
    ]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(
                color=[_hex_to_rgba(c, 0.92) for c in colors],
                line=dict(color=borders, width=1.6),
            ),
            text=[f"<b>{v:.1f} min</b>" for v in values],
            textposition="outside",
            textfont=dict(color="#0F172A", size=13, family="Inter"),
            cliponaxis=False,
            hovertext=hover_texts,
            hoverinfo="text",
            width=0.48,
            showlegend=False,
        )
    )

    # Reference at the overall mean
    fig.add_hline(
        y=overall_mean,
        line=dict(color="#94A3B8", width=1, dash="dot"),
        annotation_text=f"Overall mean · {overall_mean:.1f} min",
        annotation_position="right",
        annotation_font=dict(color="#64748B", size=10, family="Inter"),
    )

    # Dynamic delta callout — wording chosen by which side is larger
    if weekday_val > 0 and weekend_val > 0:
        diff = weekend_val - weekday_val
        if abs(diff) > 0.05:
            if diff > 0:
                headline = "Weekend rides are longer"
                delta_color = _PURPLE_DARK
            else:
                headline = "Weekday rides are longer"
                delta_color = _TEAL_DARK

            pct = abs(diff) / min(weekday_val, weekend_val) * 100.0 if min(weekday_val, weekend_val) > 0 else 0.0

            fig.add_annotation(
                xref="paper",
                yref="paper",
                x=0.5,
                y=1.14,
                text=(
                    f"<span style='color:#0F172A;font-size:12px;font-weight:700;'>{headline}</span>"
                    f" <span style='color:{delta_color};font-size:12px;font-weight:700;'>"
                    f"by {abs(diff):.2f} min ({pct:.1f}%)</span>"
                ),
                showarrow=False,
                align="center",
                bgcolor="rgba(248, 250, 252, 0.9)",
                bordercolor="#E2E8F0",
                borderwidth=1,
                borderpad=6,
            )
        else:
            fig.add_annotation(
                xref="paper",
                yref="paper",
                x=0.5,
                y=1.14,
                text=(
                    "<span style='color:#64748B;font-size:12px;font-weight:600;'>"
                    "Durations are essentially identical on weekdays and weekends"
                    "</span>"
                ),
                showarrow=False,
                align="center",
                bgcolor="rgba(248, 250, 252, 0.9)",
                bordercolor="#E2E8F0",
                borderwidth=1,
                borderpad=6,
            )

    fig = apply_chart_theme(
        fig,
        height=CHART_HEIGHT_LINE,
        margin=dict(l=14, r=60, t=64, b=36),
    )

    fig.update_layout(
        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color=_AXIS_TEXT, size=13, family="Inter"),
        ),
        yaxis=dict(
            title=dict(text="Average Duration (minutes)", font=dict(color=_AXIS_TITLE, size=11, family="Inter")),
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            rangemode="tozero",
            tickfont=dict(color=_AXIS_TEXT, size=11, family="Inter"),
        ),
        bargap=0.55,
        hoverlabel=_HOVER_LABEL,
        showlegend=False,
    )

    return fig