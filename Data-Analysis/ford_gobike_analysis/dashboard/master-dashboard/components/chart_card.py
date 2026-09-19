"""
components/chart_card.py – Unified SaaS Chart Card Container
=============================================================
Reusable container with:
  - Card header: title, subtitle, info tooltip, optional actions
  - Card body: dcc.Loading wrapping interactive dcc.Graph
  - Optional card footer: takeaway or lineage note
"""

from __future__ import annotations

from typing import Optional, List, Any
from dash import html, dcc
import plotly.graph_objects as go


def render_chart_card(
    title: str,
    graph_id: str,
    figure: Optional[go.Figure] = None,
    subtitle: Optional[str] = None,
    tooltip: Optional[str] = None,
    actions: Optional[List[Any]] = None,
    footer_text: Optional[str] = None,
    height: int = 340,
    className: str = "",
    card_id: Optional[str] = None,
    graph_config: Optional[dict] = None,
) -> html.Div:
    """
    Renders a modern, uniform chart card container for Plotly figures.
    """
    default_config = {
        "displayModeBar": "hover",
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {
            "format": "png",
            "filename": f"{graph_id}_export",
            "height": 500,
            "width": 800,
            "scale": 2,
        },
    }
    if graph_config:
        default_config.update(graph_config)

    header_children = [
        html.Div(
            className="flex flex-col",
            children=[
                html.Div(
                    className="flex items-center gap-1.5",
                    children=[
                        html.H3(title, className="text-sm sm:text-base font-semibold text-slate-800 tracking-tight"),
                        html.Span(
                            "ⓘ",
                            title=tooltip if tooltip else title,
                            className="text-slate-400 hover:text-slate-600 text-xs cursor-help select-none",
                        ) if tooltip else None,
                    ],
                ),
                html.P(subtitle, className="text-xs text-slate-500 mt-0.5") if subtitle else None,
            ],
        ),
        html.Div(
            className="flex items-center gap-2",
            children=actions if actions else [],
        ) if actions else None,
    ]
    header_filtered = [c for c in header_children if c is not None]

    card_children = [
        # Card Header
        html.Div(
            className="flex items-center justify-between pb-3 mb-2 border-b border-slate-100",
            children=header_filtered,
        ),

        # Card Body: Plotly graph wrapped in dcc.Loading
        html.Div(
            className="w-full flex-1 min-h-[200px]",
            children=[
                dcc.Loading(
                    type="dot",
                    color="#14B8A6",
                    children=dcc.Graph(
                        id=graph_id,
                        figure=figure or go.Figure(),
                        config=default_config,
                        style={"height": f"{height}px", "width": "100%"},
                    ),
                )
            ],
        ),

        # Optional Card Footer
        html.Div(
            className="pt-2 mt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400",
            children=[
                html.Span(footer_text),
                html.Span("Live Query • Supabase Gold", className="text-slate-400 font-mono text-[10px]"),
            ],
        ) if footer_text else None,
    ]

    card_filtered = [c for c in card_children if c is not None]
    div_kwargs = {"id": card_id} if card_id else {}

    return html.Div(
        className=(
            f"bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm "
            f"hover:shadow-md transition-all duration-200 flex flex-col justify-between {className}"
        ),
        children=card_filtered,
        **div_kwargs,
    )
