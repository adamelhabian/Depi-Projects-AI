"""
components/chart_card.py – Tailwind Styled Chart Card Wrapper
============================================================
Provides a clean, Tailwind CSS-styled card container matching station_trip_analysis.html:
  - Header row with bold title and status badge
  - Subtitle with explanatory description
  - Plotly Graph slot with configured clean modebar
  - Footnote at the bottom for instructions/clarifications
"""

from __future__ import annotations

from dash import dcc, html


def chart_card(
    graph_id: str,
    title: str,
    subtitle: str = "",
    badge_text: str = "",
    badge_class: str = "",
    badges: list[html.Span] | None = None,
    footnote: str = "",
    footnote_left: str = "",
    height: int = 340,
    className: str = "",
) -> html.Div:
    """
    Return a Tailwind-styled card div containing title, badge, subtitle, dcc.Graph, and footnote.
    """
    top_row_children = [
        html.H2(title, className="text-base sm:text-lg font-bold text-slate-900"),
    ]
    if badges:
        top_row_children.append(html.Div(badges, className="flex items-center gap-1.5"))
    elif badge_text:
        top_row_children.append(
            html.Span(
                badge_text,
                className=badge_class or "text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600",
            )
        )

    header = html.Div(
        className="mb-1",
        children=[
            html.Div(top_row_children, className="flex items-center justify-between mb-1"),
            html.P(subtitle, className="text-xs text-slate-500 mb-2") if subtitle else None,
        ],
    )

    footer = None
    if footnote_left and footnote:
        footer = html.Div(
            className="mt-2 flex justify-between text-[11px] text-slate-400",
            children=[
                html.Span(footnote_left),
                html.Span(footnote),
            ],
        )
    elif footnote:
        footer = html.Div(
            footnote,
            className="mt-2 text-[11px] text-slate-400 text-right",
        )

    card_children = [
        header,
        html.Div(
            style={"position": "relative", "width": "100%", "minHeight": f"{height}px"},
            children=[
                dcc.Graph(
                    id=graph_id,
                    style={"height": f"{height}px", "width": "100%"},
                    config={
                        "displayModeBar": "hover",
                        "displaylogo": False,
                        "modeBarButtonsToRemove": [
                            "select2d",
                            "lasso2d",
                            "autoScale2d",
                        ],
                    },
                ),
            ],
        ),
    ]
    if footer:
        card_children.append(footer)

    return html.Div(
        className=f"bg-white rounded-xl border border-slate-200 shadow-sm p-4 sm:p-5 flex flex-col justify-between {className}".strip(),
        children=card_children,
    )
