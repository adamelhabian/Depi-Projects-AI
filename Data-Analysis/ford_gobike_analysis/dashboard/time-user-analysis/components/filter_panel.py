"""
components/filter_panel.py – Slicers & Controls for Time & User Analytics
==========================================================================
Compact, clean Tailwind filter panel with responsive layout:
  - User Membership (All / Subscribers / Customers)
  - Day Type (All Days / Weekdays / Weekends)
"""

from __future__ import annotations

from dash import dcc, html
from config import ID_USER_FILTER, ID_DAY_FILTER


def filter_panel() -> html.Section:
    """Render a clean, focused filter panel for Time & User analysis."""
    return html.Section(
        className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-4 sm:p-5 mb-6 transition-all",
        children=[
            html.Div(
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-4 items-center",
                children=[
                    # 1. User Membership Filter
                    html.Div(
                        className="lg:col-span-6",
                        children=[
                            html.Label(
                                "Rider Membership Type",
                                className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5",
                            ),
                            dcc.Dropdown(
                                id=ID_USER_FILTER,
                                className="tu-dropdown",
                                options=[
                                    {"label": "All Riders (Combined)", "value": "All"},
                                    {"label": "Subscribers (Commuter Members)", "value": "Subscriber"},
                                    {"label": "Casual (Day Pass / Non-Member)", "value": "Customer"},
                                ],
                                value="All",
                                clearable=False,
                                searchable=False,
                            ),
                        ],
                    ),

                    # 2. Day Classification Filter
                    html.Div(
                        className="lg:col-span-6",
                        children=[
                            html.Label(
                                "Temporal Day Classification",
                                className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5",
                            ),
                            dcc.Dropdown(
                                id=ID_DAY_FILTER,
                                className="tu-dropdown",
                                options=[
                                    {"label": "All Days (Monday – Sunday)", "value": "All"},
                                    {"label": "Weekdays Only (Monday – Friday)", "value": "Weekday"},
                                    {"label": "Weekends Only (Saturday – Sunday)", "value": "Weekend"},
                                ],
                                value="All",
                                clearable=False,
                                searchable=False,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
