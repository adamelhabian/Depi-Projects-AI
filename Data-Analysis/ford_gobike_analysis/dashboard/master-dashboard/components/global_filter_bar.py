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
    ID_GLOBAL_RESET_BTN,
    ID_GLOBAL_CHIPS,
    ID_GLOBAL_STORE,
    GLOBAL_FILTER_DEFAULTS,
    USER_FILTER_LABELS,
    REGION_FILTER_LABELS,
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
            "All Filters Active",
            className="text-[11px] text-slate-400 italic",
        )
    ]


def render_global_filter_bar() -> html.Div:
    """
    Renders the sticky global filter bar.
    The dcc.Store is also mounted here so it travels with every page.
    """
    return html.Div(
        # sticky under the navbar (top = 64px = navbar height ≈ 4rem)
        className="sticky top-0 z-20 bg-white/95 backdrop-blur-sm border-b border-slate-200 shadow-xs",
        children=[
            dcc.Store(
                id=ID_GLOBAL_STORE,
                storage_type="session",          # survives page nav, cleared on tab close
                data=GLOBAL_FILTER_DEFAULTS,
            ),

            html.Div(
                className="flex flex-wrap items-center gap-3 px-6 py-3",
                children=[
                    # ── Label ────────────────────────────────────────────────
                    html.Span(
                        "Global Filters",
                        className="text-[10px] font-black uppercase tracking-widest text-slate-400 shrink-0",
                    ),

                    # ── Rider Membership Dropdown ─────────────────────────
                    html.Div(
                        className="flex flex-col gap-0.5 min-w-[180px]",
                        children=[
                            html.Label(
                                "Rider Type",
                                htmlFor=ID_GLOBAL_USER_FILTER,
                                className="text-[10px] font-bold uppercase tracking-wider text-slate-400",
                            ),
                            dcc.Dropdown(
                                id=ID_GLOBAL_USER_FILTER,
                                options=[
                                    {"label": "All Riders (Combined)",               "value": "All"},
                                    {"label": "Subscribers (Commuter Members)",       "value": "Subscriber"},
                                    {"label": "Customers (Casual / Day Pass)",        "value": "Customer"},
                                ],
                                value=GLOBAL_FILTER_DEFAULTS["user_type"],
                                clearable=False,
                                searchable=False,
                                style={"fontSize": "12px"},
                            ),
                        ],
                    ),

                    # ── Metro Region Dropdown ─────────────────────────────
                    html.Div(
                        className="flex flex-col gap-0.5 min-w-[190px]",
                        children=[
                            html.Label(
                                "Metro Region",
                                htmlFor=ID_GLOBAL_REGION_FILTER,
                                className="text-[10px] font-bold uppercase tracking-wider text-slate-400",
                            ),
                            dcc.Dropdown(
                                id=ID_GLOBAL_REGION_FILTER,
                                options=[
                                    {"label": "All Bay Area (329 Stns)",               "value": "All"},
                                    {"label": "San Francisco (156 Stns)",               "value": "San Francisco"},
                                    {"label": "East Bay – Oakland / Berkeley (127 Stns)","value": "East Bay (Oakland/Berkeley)"},
                                    {"label": "San Jose (46 Stns)",                     "value": "San Jose"},
                                ],
                                value=GLOBAL_FILTER_DEFAULTS["region"],
                                clearable=False,
                                searchable=False,
                                style={"fontSize": "12px"},
                            ),
                        ],
                    ),

                    # ── Active Filter Chips ───────────────────────────────
                    html.Div(
                        id=ID_GLOBAL_CHIPS,
                        className="flex flex-wrap items-center gap-1.5 flex-1",
                        children=_initial_chips(),
                    ),

                    # ── Reset All Button ──────────────────────────────────
                    html.Button(
                        [
                            html.I(className="fas fa-rotate-left text-[10px] mr-1"),
                            "Reset",
                        ],
                        id=ID_GLOBAL_RESET_BTN,
                        n_clicks=0,
                        className="ml-auto shrink-0 text-[11px] font-semibold text-slate-500 hover:text-slate-800 border border-slate-200 hover:border-slate-400 px-3 py-1.5 rounded-lg transition-colors bg-white",
                        title="Reset all filters to defaults",
                    ),
                ],
            ),
        ],
    )
