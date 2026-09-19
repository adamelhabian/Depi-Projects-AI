"""
components/kpi_card.py – SaaS Metric Card Component
====================================================
Standard executive KPI metric card with:
  - Header with title label, tooltip icon, and category icon
  - High-visibility primary metric value
  - Delta badge showing trend/variance with color semantics
  - Plotly micro-sparkline
"""

from __future__ import annotations

from typing import List, Optional
from dash import html, dcc
import plotly.graph_objects as go
from utils.theme import make_sparkline_fig, COLORS


def render_kpi_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_type: str = "positive",  # 'positive', 'negative', 'neutral', 'purple', 'blue'
    subtext: str = "",
    sparkline_data: Optional[List[float]] = None,
    sparkline_color: str = "#14B8A6",
    tooltip: str = "",
    icon_class: str = "fas fa-chart-bar",
    card_id: Optional[str] = None,
) -> html.Div:
    """
    Builds an enterprise SaaS KPI card.
    """
    if delta_type == "positive":
        badge_cls = "bg-teal-50 text-teal-700 border-teal-200"
        arrow = "↑"
    elif delta_type == "negative":
        badge_cls = "bg-amber-50 text-amber-700 border-amber-200"
        arrow = "↓"
    elif delta_type == "purple":
        badge_cls = "bg-purple-50 text-purple-700 border-purple-200"
        arrow = "⚡"
    elif delta_type == "blue":
        badge_cls = "bg-blue-50 text-blue-700 border-blue-200"
        arrow = "✦"
    else:
        badge_cls = "bg-slate-50 text-slate-600 border-slate-200"
        arrow = "•"

    sparkline_fig = None
    if sparkline_data:
        fill_color = "rgba(20, 184, 166, 0.12)" if sparkline_color == "#14B8A6" else "rgba(168, 85, 247, 0.12)"
        sparkline_fig = make_sparkline_fig(sparkline_data, color=sparkline_color, fill_rgba=fill_color)

    children = [
        # Top row: Label + Tooltip icon + Accent Icon
        html.Div(
            className="flex items-center justify-between text-slate-500 mb-2",
            children=[
                html.Div(
                    className="flex items-center gap-1.5",
                    children=[
                        html.Span(title, className="text-xs font-semibold uppercase tracking-wider text-slate-600"),
                        html.Span(
                            "ⓘ",
                            title=tooltip if tooltip else title,
                            className="text-slate-400 hover:text-slate-600 text-xs cursor-help select-none",
                        ) if tooltip else None,
                    ],
                ),
                html.Div(
                    className="w-7 h-7 rounded-lg bg-slate-100 flex items-center justify-center text-slate-500 text-xs",
                    children=[html.I(className=icon_class)],
                ),
            ],
        ),

        # Middle row: Primary Large Value + Sparkline
        html.Div(
            className="flex items-baseline justify-between mt-1 mb-3",
            children=[
                html.Span(value, className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900"),
                html.Div(
                    className="w-20 h-7 flex-shrink-0",
                    children=[
                        dcc.Graph(
                            figure=sparkline_fig,
                            config={"displayModeBar": False, "staticPlot": True},
                            style={"height": "28px", "width": "80px"},
                        )
                    ],
                ) if sparkline_fig else None,
            ],
        ),

        # Bottom row: Delta badge + Subtext
        html.Div(
            className="flex items-center gap-2 text-xs",
            children=[
                html.Span(
                    f"{arrow} {delta}" if delta else "",
                    className=f"inline-flex items-center px-2 py-0.5 rounded-full font-medium border text-[11px] {badge_cls}",
                ) if delta else None,
                html.Span(subtext, className="text-slate-500 text-xs truncate") if subtext else None,
            ],
        ),
    ]

    filtered_children = [c for c in children if c is not None]
    div_kwargs = {"id": card_id} if card_id else {}

    return html.Div(
        className=(
            "bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm "
            "hover:shadow-md transition-all duration-200 flex flex-col justify-between"
        ),
        children=filtered_children,
        **div_kwargs,
    )
