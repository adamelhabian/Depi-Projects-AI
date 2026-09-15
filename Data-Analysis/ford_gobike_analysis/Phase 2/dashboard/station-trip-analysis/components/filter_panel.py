"""
components/filter_panel.py – Comprehensive Filter & Export Controls
====================================================================
Interactive control panel for:
  - User Membership (All, Subscriber, Customer)
  - Metro Region (All Bay Area, San Francisco, East Bay, San Jose)
  - Top N Rankings Slider (Applies to ranking charts)
  - Flow Corridor Lines Toggle (On-map transit corridors)
  - CSV Dataset Export (Downloads current canonical station metrics)
"""

from __future__ import annotations

from dash import dcc, html
from config import (
    ID_USER_FILTER,
    ID_TOP_N_SLIDER,
    ID_REGION_FILTER,
    ID_MAP_FLOW_LINES_TOGGLE,
    ID_DOWNLOAD_BTN,
    ID_DOWNLOAD_DATA,
    DEFAULT_TOP_N,
    TOP_N_MIN,
    TOP_N_MAX,
    TOP_N_STEP,
    COLORS,
)


def filter_panel() -> html.Div:
    """
    Build the Station & Trip Analysis filter bar.

    Returns
    -------
    html.Div
    """
    slider_marks = {
        n: {
            "label": f"Top {n}",
            "style": {"color": COLORS["text_muted"], "fontSize": "11px"},
        }
        for n in range(TOP_N_MIN, TOP_N_MAX + 1, TOP_N_STEP)
    }

    return html.Div(
        className="filter-panel",
        children=[
            # Row 1: Primary Controls & Export
            html.Div(
                className="filter-main-row",
                children=[
                    # Section Tag
                    html.Div(
                        className="filter-tag-container",
                        children=[
                            html.Span("CONTROLS", className="filter-badge"),
                        ],
                    ),

                    # User Membership Filter
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("User Membership", className="filter-label"),
                            dcc.Dropdown(
                                id=ID_USER_FILTER,
                                className="m5-dropdown",
                                options=[
                                    {"label": "All Users", "value": "All"},
                                    {"label": "Subscribers", "value": "Subscriber"},
                                    {"label": "Customers", "value": "Customer"},
                                ],
                                value="All",
                                clearable=False,
                                searchable=False,
                                style={"width": "165px"},
                            ),
                        ],
                    ),

                    # Metro Region Filter
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Metro Region", className="filter-label"),
                            dcc.Dropdown(
                                id=ID_REGION_FILTER,
                                className="m5-dropdown",
                                options=[
                                    {"label": "All Bay Area (329 Stns)", "value": "All"},
                                    {"label": "San Francisco (156 Stns)", "value": "San Francisco"},
                                    {"label": "East Bay (127 Stns)", "value": "East Bay (Oakland/Berkeley)"},
                                    {"label": "San Jose (46 Stns)", "value": "San Jose"},
                                ],
                                value="All",
                                clearable=False,
                                searchable=False,
                                style={"width": "230px"},
                            ),
                        ],
                    ),

                    # Map Corridor Lines Toggle
                    html.Div(
                        className="filter-group toggle-group",
                        children=[
                            html.Label("Map Overlays", className="filter-label"),
                            dcc.Checklist(
                                id=ID_MAP_FLOW_LINES_TOGGLE,
                                options=[
                                    {"label": " Flow Corridors", "value": "show"},
                                ],
                                value=["show"],
                                className="m5-checklist",
                            ),
                        ],
                    ),

                    # Export Button & Download Target
                    html.Div(
                        className="filter-group export-group",
                        style={"marginLeft": "auto"},
                        children=[
                            html.Label("Data Export", className="filter-label"),
                            html.Button(
                                [
                                    html.Span("📥", style={"marginRight": "6px"}),
                                    "Export CSV",
                                ],
                                id=ID_DOWNLOAD_BTN,
                                className="btn-export",
                                n_clicks=0,
                            ),
                            dcc.Download(id=ID_DOWNLOAD_DATA),
                        ],
                    ),
                ],
            ),

            # Row 2: Top N Ranking Filter with clarifying scope note
            html.Div(
                className="filter-slider-row",
                children=[
                    html.Div(
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "baseline", "marginBottom": "4px"},
                        children=[
                            html.Label("Top N Stations & Corridors", className="filter-label"),
                            html.Span(
                                "Applies to ranking charts · Map displays all active stations in selected region",
                                className="filter-hint",
                            ),
                        ],
                    ),
                    dcc.Slider(
                        id=ID_TOP_N_SLIDER,
                        min=TOP_N_MIN,
                        max=TOP_N_MAX,
                        step=TOP_N_STEP,
                        value=DEFAULT_TOP_N,
                        marks=slider_marks,
                    ),
                ],
            ),
        ],
    )
