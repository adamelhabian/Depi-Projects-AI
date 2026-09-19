"""
utils/theme.py – Reusable Plotly Theme & Empty State Helpers
============================================================
Centralizes all Plotly layout rules across Member 5 charts.
Ensures identical backgrounds, fonts, margins, gridlines, and hover styling.
"""

from __future__ import annotations

import plotly.graph_objects as go
from config import COLORS, FONT_FAMILY


def apply_chart_theme(
    fig: go.Figure,
    height: int = 380,
    margin: dict | None = None,
    show_grid: bool = True,
) -> go.Figure:
    """
    Apply the unified dark BI theme to any Plotly figure.

    Parameters
    ----------
    fig : go.Figure
        The Plotly figure to style.
    height : int
        Figure height in pixels.
    margin : dict, optional
        Custom margins; defaults to balanced margins.
    show_grid : bool
        Whether to display subtle vertical gridlines.

    Returns
    -------
    go.Figure
    """
    default_margin = dict(l=16, r=24, t=20, b=24)
    if margin:
        default_margin.update(margin)

    fig.update_layout(
        paper_bgcolor=COLORS["bg_card"],
        plot_bgcolor=COLORS["bg_card"],
        height=height,
        margin=default_margin,
        font=dict(
            family=FONT_FAMILY,
            color=COLORS["text_muted"],
            size=12,
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor=COLORS["border"],
            font=dict(
                family=FONT_FAMILY,
                color=COLORS["text_main"],
                size=12,
            ),
        ),
        xaxis=dict(
            gridcolor="#F1F5F9" if show_grid else "rgba(0,0,0,0)",
            linecolor=COLORS["border"],
            tickfont=dict(color=COLORS["text_muted"], size=11),
            title_font=dict(color=COLORS["text_main"], size=12),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0)",
            linecolor=COLORS["border"],
            tickfont=dict(color=COLORS["text_muted"], size=11),
            title_font=dict(color=COLORS["text_main"], size=12),
            zeroline=False,
            automargin=True,
        ),
        showlegend=False,
    )
    return fig


def empty_figure(message: str, height: int = 380) -> go.Figure:
    """
    Return a clean empty-state figure displaying a centered message.
    Prevents unhandled exceptions or broken Plotly containers when data is empty.

    Parameters
    ----------
    message : str
        Human-readable message explaining why no data is shown.
    height : int
        Figure height in pixels.

    Returns
    -------
    go.Figure
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(
            family=FONT_FAMILY,
            size=13,
            color=COLORS["text_muted"],
        ),
        align="center",
    )
    fig.update_layout(
        paper_bgcolor=COLORS["bg_card"],
        plot_bgcolor=COLORS["bg_card"],
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig