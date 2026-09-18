"""
components/filter_panel.py – Tailwind CSS Controls Bar
======================================================
12-column grid controls bar matching station_trip_analysis.html:
  - User Membership Dropdown (col-span-3)
  - Metro Region Dropdown (col-span-3)
  - Top Ranking Scope Slider (col-span-3)
  - Flow Corridors Toggle & Dark CSV Export Button (col-span-3)
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
)
from components.icons import icon_download



def filter_panel() -> html.Section:
    """
    Render the 12-column Tailwind-styled filter panel controls bar.
    """
    benchmark_marks = [1, 5, 10, 15, 20, 25, 30]
    slider_marks = {
        i: {"label": str(i), "style": {"color": "#64748B", "fontSize": "11px", "fontWeight": "600"}}
        for i in benchmark_marks
    }

    return html.Section(
        className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 sm:p-5 mb-6 transition-all",
        children=[
            html.Div(
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-4 items-center",
                children=[
                    # ── 1. User Membership Filter (Col 3) ─────────────────
                    html.Div(
                        className="lg:col-span-3",
                        children=[
                            html.Label(
                                "User Membership",
                                className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5",
                            ),
                            dcc.Dropdown(
                                id=ID_USER_FILTER,
                                className="m5-dropdown",
                                options=[
                                    {"label": "All Users (Total Volume)", "value": "All"},
                                    {"label": "Subscriber (Annual / Pass)", "value": "Subscriber"},
                                    {"label": "Customer (Casual / 24h Pass)", "value": "Customer"},
                                ],
                                value="All",
                                clearable=False,
                                searchable=False,
                                style={"width": "100%"},
                            ),
                        ],
                    ),

                    # ── 2. Metro Region Filter (Col 3) ────────────────────
                    html.Div(
                        className="lg:col-span-3",
                        children=[
                            html.Label(
                                "Metro Region",
                                className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5",
                            ),
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
                                style={"width": "100%"},
                            ),
                        ],
                    ),

                    # ── 3. Top Ranking Scope Slider (Col 3) ───────────────
                    html.Div(
                        className="lg:col-span-3",
                        children=[
                            html.Div(
                                className="flex justify-between items-center mb-1.5",
                                children=[
                                    html.Label(
                                        "Top Ranking Scope",
                                        className="text-xs font-semibold uppercase tracking-wider text-slate-500",
                                    ),
                                    html.Span(
                                        f"Top {DEFAULT_TOP_N}",
                                        id="m5-slider-scope-badge",
                                        className="text-xs font-bold text-teal-700 bg-teal-50 border border-teal-200 px-2 py-0.5 rounded-full",
                                    ),
                                ],
                            ),
                            html.Div(
                                style={"padding": "0 6px"},
                                children=[
                                    dcc.Slider(
                                        id=ID_TOP_N_SLIDER,
                                        min=TOP_N_MIN,
                                        max=TOP_N_MAX,
                                        step=TOP_N_STEP,
                                        value=DEFAULT_TOP_N,
                                        marks=slider_marks,
                                        tooltip={"placement": "bottom", "always_visible": False},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # ── 4. Flow Corridors Switch & Export CSV (Col 3) ──────
                    html.Div(
                        className="lg:col-span-3 flex flex-wrap sm:flex-nowrap items-center justify-between sm:justify-end gap-3 pt-2 lg:pt-0",
                        children=[
                            # Corridor Toggle
                            dcc.Checklist(
                                id=ID_MAP_FLOW_LINES_TOGGLE,
                                options=[
                                    {"label": " Flow Corridors", "value": "show"},
                                ],
                                value=["show"],
                                className="m5-checklist text-xs font-medium text-slate-700 cursor-pointer",
                            ),

                            # Export CSV Button
                            html.Button(
                                [
                                    icon_download("w-3.5 h-3.5 mr-1.5 inline-block"),
                                    "Export CSV",
                                ],
                                id=ID_DOWNLOAD_BTN,
                                className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-white shadow transition active:scale-95 cursor-pointer",
                                n_clicks=0,
                            ),
                            dcc.Download(id=ID_DOWNLOAD_DATA),
                        ],
                    ),
                ],
            ),
        ],
    )
