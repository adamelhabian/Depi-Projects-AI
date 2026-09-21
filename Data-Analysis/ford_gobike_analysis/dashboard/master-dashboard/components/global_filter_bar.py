"""
components/global_filter_bar.py – Persistent Global Filter Bar
==============================================================
A sticky filter bar rendered at the top of every page inside the master dashboard.
Stores selections in dcc.Store (`master-global-filter-store`) so values
persist across page navigation.

Controls:
  - Rider Membership dropdown  (All / Subscriber / Customer)
  - Metro Region dropdown      (All / SF / East Bay / San Jose)
  - Active-filter chips row    (shows current values, auto-hides "All" chips)
  - Reset All button           (clears both dropdowns back to defaults)
"""

from __future__ import annotations

from dash import dcc, html
from config import (
    ID_GLOBAL_USER_FILTER,
    ID_GLOBAL_REGION_FILTER,
    ID_GLOBAL_GENDER_FILTER,
    ID_GLOBAL_DAY_FILTER,
    ID_GLOBAL_RESET_BTN,
    ID_GLOBAL_CHIPS,
    ID_GLOBAL_STORE,
    GLOBAL_FILTER_DEFAULTS,
    USER_FILTER_LABELS,
    REGION_FILTER_LABELS,
    GENDER_FILTER_LABELS,
    DAY_FILTER_LABELS,
)


def _chip(label: str, color_class: str) -> html.Span:
    """One small active-filter pill."""
    return html.Span(
        className=f"inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border {color_class}",
        children=label,
    )


def _initial_chips() -> list:
    """Chips shown on first render (all defaults → only show a neutral 'All Filters' chip)."""
    return [
        html.Span(
            "No active filters applied",
            className="text-[11px] text-slate-400 italic",
        )
    ]


def render_global_filter_bar() -> html.Div:
    """
    Renders the sticky global filter bar with 4 master slicers + timeframe.
    The dcc.Store is also mounted here so it travels with every page.
    """
    return html.Div(
        className="master-filter-bar-sticky sticky top-14 z-20 bg-white/95 backdrop-blur-sm border-b border-slate-200 shadow-2xs",
        style={"top": "56px"},
        children=[
            dcc.Store(
                id=ID_GLOBAL_STORE,
                storage_type="session",
                data=GLOBAL_FILTER_DEFAULTS,
            ),

            html.Div(
                className="flex flex-wrap items-center gap-3.5 px-6 py-2.5",
                children=[
                    # ── 1. TIMEFRAME Segmented Control ────────────────────
                    html.Div(
                        className="flex items-center gap-1.5",
                        title="30D & 90D are disabled because the dataset spans 28 days (Feb 2019). Full window captured under ALL.",
                        children=[
                            html.Span(
                                "TIME:",
                                className="text-[10px] font-black uppercase tracking-wider text-slate-400 shrink-0",
                            ),
                            dcc.RadioItems(
                                id="global-timeframe-filter",
                                options=[
                                    {"label": "7D", "value": "7d"},
                                    {"label": "30D", "value": "30d", "disabled": True},
                                    {"label": "90D", "value": "90d", "disabled": True},
                                    {"label": "ALL", "value": "all"},
                                ],
                                value="all",
                                inline=True,
                                className="timeframe-segmented-control",
                            ),
                        ],
                    ),

                    # ── 2. RIDER TYPE Dropdown ────────────────────────────
                    html.Div(
                        className="flex items-center gap-1.5 min-w-[160px]",
                        children=[
                            html.Span(
                                "RIDER:",
                                className="text-[10px] font-black uppercase tracking-wider text-slate-400 shrink-0",
                            ),
                            html.Div(
                                className="flex-1",
                                children=[
                                    dcc.Dropdown(
                                        id=ID_GLOBAL_USER_FILTER,
                                        options=[
                                            {"label": "All Memberships", "value": "All"},
                                            {"label": "Subscriber",      "value": "Subscriber"},
                                            {"label": "Casual",          "value": "Customer"},
                                        ],
                                        value=GLOBAL_FILTER_DEFAULTS["user_type"],
                                        clearable=False,
                                        searchable=False,
                                        style={"fontSize": "12px", "minHeight": "32px"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # ── 3. METRO REGION Dropdown ──────────────────────────
                    html.Div(
                        className="flex items-center gap-1.5 min-w-[185px]",
                        children=[
                            html.Span(
                                "REGION:",
                                className="text-[10px] font-black uppercase tracking-wider text-slate-400 shrink-0",
                            ),
                            html.Div(
                                className="flex-1",
                                children=[
                                    dcc.Dropdown(
                                        id=ID_GLOBAL_REGION_FILTER,
                                        options=[
                                            {"label": "All Bay Area",                         "value": "All"},
                                            {"label": "San Francisco",                        "value": "San Francisco"},
                                            {"label": "East Bay (Oakland/Berkeley)",          "value": "East Bay (Oakland/Berkeley)"},
                                            {"label": "San Jose",                             "value": "San Jose"},
                                        ],
                                        value=GLOBAL_FILTER_DEFAULTS["region"],
                                        clearable=False,
                                        searchable=False,
                                        style={"fontSize": "12px", "minHeight": "32px"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # ── 4. RIDER GENDER Dropdown (New Filter 1) ───────────
                    html.Div(
                        className="flex items-center gap-1.5 min-w-[150px]",
                        children=[
                            html.Span(
                                "GENDER:",
                                className="text-[10px] font-black uppercase tracking-wider text-slate-400 shrink-0",
                            ),
                            html.Div(
                                className="flex-1",
                                children=[
                                    dcc.Dropdown(
                                        id=ID_GLOBAL_GENDER_FILTER,
                                        options=[
                                            {"label": "All Genders", "value": "All"},
                                            {"label": "Male",        "value": "Male"},
                                            {"label": "Female",      "value": "Female"},
                                            {"label": "Other",       "value": "Other"},
                                        ],
                                        value=GLOBAL_FILTER_DEFAULTS["gender"],
                                        clearable=False,
                                        searchable=False,
                                        style={"fontSize": "12px", "minHeight": "32px"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # ── 5. DAY TYPE Dropdown (New Filter 2) ───────────────
                    html.Div(
                        className="flex items-center gap-1.5 min-w-[150px]",
                        children=[
                            html.Span(
                                "DAY:",
                                className="text-[10px] font-black uppercase tracking-wider text-slate-400 shrink-0",
                            ),
                            html.Div(
                                className="flex-1",
                                children=[
                                    dcc.Dropdown(
                                        id=ID_GLOBAL_DAY_FILTER,
                                        options=[
                                            {"label": "All Days", "value": "All"},
                                            {"label": "Weekday",  "value": "Weekday"},
                                            {"label": "Weekend",  "value": "Weekend"},
                                        ],
                                        value=GLOBAL_FILTER_DEFAULTS["day_type"],
                                        clearable=False,
                                        searchable=False,
                                        style={"fontSize": "12px", "minHeight": "32px"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # ── 6. Reset Button ───────────────────────────────────
                    html.Button(
                        [
                            html.I(className="fas fa-rotate-left text-[10px] mr-1 text-rose-500"),
                            html.Span("Reset", className="text-rose-600 font-semibold"),
                        ],
                        id=ID_GLOBAL_RESET_BTN,
                        n_clicks=0,
                        className="flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-lg hover:bg-rose-50 transition-colors bg-transparent border border-rose-200/60 cursor-pointer",
                        title="Reset all 4 filters to default values",
                    ),

                    # ── 7. Active Filter Status / Chips ───────────────────
                    html.Div(
                        id=ID_GLOBAL_CHIPS,
                        className="ml-auto text-xs text-slate-400 italic flex items-center gap-1.5 flex-wrap",
                        children=[
                            html.Span("No active filters applied"),
                        ],
                    ),
                ],
            ),
        ],
    )
