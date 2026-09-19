"""
components/global_filter_bar.py – Persistent Executive Global Filter Bar
========================================================================
Sticky top filter bar with:
  - Timeframe selector (All / Weekday / Weekend)
  - User type filter (All / Subscriber / Customer)
  - Region filter (All / San Francisco / East Bay / San Jose)
  - Active filter chips showing current selections with "Reset all"
  - State synced via dcc.Store(id="master-global-filters", storage_type="session")
"""

from __future__ import annotations

from dash import dcc, html
from config import (
    ID_GLOBAL_STORE,
    ID_GLOBAL_TIMEFRAME,
    ID_GLOBAL_USER_FILTER,
    ID_GLOBAL_REGION_FILTER,
    ID_GLOBAL_RESET_BTN,
    ID_GLOBAL_CHIPS,
    GLOBAL_FILTER_DEFAULTS,
)


def render_global_filter_bar() -> html.Div:
    """
    Renders the sticky global filter bar with backdrop blur and uniform styling.
    """
    return html.Div(
        className="sticky top-0 z-20 bg-white/80 backdrop-blur-md border-b border-slate-200 px-6 py-3 shadow-xs",
        children=[
            # Persistent session store
            dcc.Store(
                id=ID_GLOBAL_STORE,
                storage_type="session",
                data=GLOBAL_FILTER_DEFAULTS,
            ),

            html.Div(
                className="flex flex-wrap items-center gap-4 justify-between",
                children=[
                    # Left Controls Group
                    html.Div(
                        className="flex flex-wrap items-center gap-3",
                        children=[
                            html.Span(
                                "Filters",
                                className="text-[10px] font-bold uppercase tracking-wider text-slate-400 select-none mr-1",
                            ),

                            # 1. Timeframe Filter
                            html.Div(
                                className="w-36",
                                children=[
                                    dcc.Dropdown(
                                        id=ID_GLOBAL_TIMEFRAME,
                                        options=[
                                            {"label": "All Days", "value": "All"},
                                            {"label": "Weekdays Only", "value": "Weekday"},
                                            {"label": "Weekends Only", "value": "Weekend"},
                                        ],
                                        value=GLOBAL_FILTER_DEFAULTS.get("timeframe", "All"),
                                        clearable=False,
                                        searchable=False,
                                        style={"fontSize": "12px"},
                                    ),
                                ],
                            ),

                            # 2. User Type Filter
                            html.Div(
                                className="w-40",
                                children=[
                                    dcc.Dropdown(
                                        id=ID_GLOBAL_USER_FILTER,
                                        options=[
                                            {"label": "All Riders", "value": "All"},
                                            {"label": "Subscribers (90.5%)", "value": "Subscriber"},
                                            {"label": "Casual Customers", "value": "Customer"},
                                        ],
                                        value=GLOBAL_FILTER_DEFAULTS.get("user_type", "All"),
                                        clearable=False,
                                        searchable=False,
                                        style={"fontSize": "12px"},
                                    ),
                                ],
                            ),

                            # 3. Region Filter
                            html.Div(
                                className="w-44",
                                children=[
                                    dcc.Dropdown(
                                        id=ID_GLOBAL_REGION_FILTER,
                                        options=[
                                            {"label": "All Bay Area", "value": "All"},
                                            {"label": "San Francisco", "value": "San Francisco"},
                                            {"label": "East Bay", "value": "East Bay"},
                                            {"label": "San Jose", "value": "San Jose"},
                                        ],
                                        value=GLOBAL_FILTER_DEFAULTS.get("region", "All"),
                                        clearable=False,
                                        searchable=False,
                                        style={"fontSize": "12px"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Right Controls Group: Active Chips & Reset Button
                    html.Div(
                        className="flex items-center gap-3",
                        children=[
                            # Active Filter Chips
                            html.Div(
                                id=ID_GLOBAL_CHIPS,
                                className="flex flex-wrap items-center gap-1.5 text-xs",
                                children=[
                                    html.Span(
                                        "All Data View Active",
                                        className="text-[11px] text-slate-400 italic",
                                    )
                                ],
                            ),

                            # Reset Button
                            html.Button(
                                [
                                    html.I(className="fas fa-rotate-left text-[10px] mr-1.5"),
                                    "Reset all",
                                ],
                                id=ID_GLOBAL_RESET_BTN,
                                n_clicks=0,
                                className=(
                                    "text-xs font-medium text-slate-600 hover:text-slate-900 "
                                    "bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg "
                                    "transition-colors flex items-center border border-slate-200"
                                ),
                                title="Reset all filters to defaults",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
