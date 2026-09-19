"""
utils/theme.py – Shared Plotly Theme & Color System
===================================================
Defines the unified SaaS design tokens, WCAG AA colorblind-safe palette,
and the apply_chart_theme helper used across all Plotly figures in the dashboard.
"""

from __future__ import annotations

import plotly.graph_objects as go
from typing import Optional, Dict, Any, List

# ---------------------------------------------------------------------------
# 1. Color Palette Tokens (Matching Tailwind SaaS Theme)
# ---------------------------------------------------------------------------
COLORS = {
    # Brand Accents & Semantic Roles
    "subscriber": "#14B8A6",       # Primary Teal (Subscribers, 90.5% base)
    "subscriber_dark": "#0F766E",  # Darker Teal for borders & text
    "subscriber_soft": "rgba(20, 184, 166, 0.12)",

    "customer": "#A855F7",         # Purple (Casual Customers, 9.5% base)
    "customer_dark": "#7E22CE",    # Darker Purple for borders & text
    "customer_soft": "rgba(168, 85, 247, 0.12)",

    "surplus": "#3B82F6",          # Blue (Net Surplus / Dock saturation)
    "surplus_dark": "#1D4ED8",
    "surplus_soft": "rgba(59, 130, 246, 0.14)",

    "deficit": "#F97316",          # Orange/Coral (Net Deficit / Dock depletion)
    "deficit_dark": "#C2410C",
    "deficit_soft": "rgba(249, 115, 22, 0.14)",

    "balanced": "#94A3B8",         # Neutral Slate
    "balanced_soft": "rgba(148, 163, 184, 0.15)",

    # Surfaces & Typography
    "bg_card": "rgba(0,0,0,0)",    # Transparent so it adopts card container
    "grid": "#EEF2F6",             # Subtle reference lines
    "text_main": "#0F172A",        # Slate 900
    "text_muted": "#64748B",       # Slate 500
    "text_subtle": "#94A3B8",      # Slate 400

    # Tooltips
    "tooltip_bg": "#0F172A",       # Dark Slate tooltip
    "tooltip_border": "rgba(255, 255, 255, 0.12)",
}

FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


# ---------------------------------------------------------------------------
# 2. Shared Plotly Theme Applier
# ---------------------------------------------------------------------------
def apply_chart_theme(
    fig: go.Figure,
    height: int = 320,
    margin: Optional[Dict[str, int]] = None,
    show_legend: bool = False,
) -> go.Figure:
    """
    Applies the shared enterprise Plotly styling:
      - Clean transparent canvas
      - Inter typography
      - Subtle gridlines and zero lines
      - High-contrast executive tooltips
    """
    if margin is None:
        margin = dict(l=45, r=20, t=25, b=35)

    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=11, color=COLORS["text_muted"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=margin,
        showlegend=show_legend,
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=COLORS["tooltip_bg"],
            bordercolor=COLORS["tooltip_border"],
            font=dict(family=FONT_FAMILY, size=12, color="#FFFFFF"),
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#E2E8F0",
        tickfont=dict(family=FONT_FAMILY, size=10, color=COLORS["text_muted"]),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLORS["grid"],
        zeroline=False,
        linecolor="#E2E8F0",
        tickfont=dict(family=FONT_FAMILY, size=10, color=COLORS["text_muted"]),
    )

    return fig


def empty_figure(message: str, height: int = 320) -> go.Figure:
    """Returns a clean empty state Plotly figure with a friendly notice."""
    fig = go.Figure()
    fig.add_annotation(
        text=f"<b>Notice</b><br><span style='font-size:12px;color:#64748B;'>{message}</span>",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(family=FONT_FAMILY, size=14, color=COLORS["text_main"]),
        align="center",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


def make_sparkline_fig(
    y_values: List[float],
    color: str = "#14B8A6",
    fill_rgba: str = "rgba(20, 184, 166, 0.15)",
) -> go.Figure:
    """
    Creates an ultra-lightweight Plotly micro-sparkline figure for KPI cards.
    """
    if not y_values or len(y_values) < 2:
        y_values = [10, 12, 11, 14, 13, 16, 15]

    fig = go.Figure(
        go.Scatter(
            y=y_values,
            mode="lines",
            line=dict(color=color, width=2, shape="spline"),
            fill="tozeroy",
            fillcolor=fill_rgba,
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=24,
        width=70,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
