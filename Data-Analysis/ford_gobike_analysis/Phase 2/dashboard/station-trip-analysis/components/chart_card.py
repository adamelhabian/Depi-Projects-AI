"""
components/chart_card.py – Reusable Chart Card Wrapper
=======================================================
Provides a clean, styled container for Plotly charts with unified headings,
subtitles, and responsive card styling.
"""

from __future__ import annotations

from dash import dcc, html


def chart_card(
    graph_id: str,
    title: str,
    subtitle: str = "",
    height: int = 380,
    className: str = "",
) -> html.Div:
    """
    Return a styled card div containing title, subtitle, and dcc.Graph slot.

    Parameters
    ----------
    graph_id : str
        Unique component ID for the dcc.Graph.
    title : str
        Card heading.
    subtitle : str, optional
        Secondary explanatory text.
    height : int
        Graph height in pixels.
    className : str, optional
        Additional CSS classes.

    Returns
    -------
    html.Div
    """
    header_elements = [
        html.H3(title, className="card-title"),
    ]
    if subtitle:
        header_elements.append(html.P(subtitle, className="card-subtitle"))

    card_classes = f"dashboard-card {className}".strip()

    return html.Div(
        className=card_classes,
        children=[
            html.Div(header_elements, className="card-header"),
            dcc.Graph(
                id=graph_id,
                style={"minHeight": f"{height}px", "width": "100%"},
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
    )
