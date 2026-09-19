"""
callbacks/global_filter_callbacks.py – Global Filter State Controller
======================================================================
Manages the master-global-filters (dcc.Store) and associated UI:
  1. Store Update: Syncs Timeframe + User Type + Region dropdowns -> Store dict
  2. Reset Button: Clears all dropdowns back to "All"
  3. Chip Renderer: Draws active-filter pills from Store values
"""

from __future__ import annotations

import logging
from dash import Input, Output, State, html, callback_context, no_update

from config import (
    ID_GLOBAL_STORE,
    ID_GLOBAL_TIMEFRAME,
    ID_GLOBAL_USER_FILTER,
    ID_GLOBAL_REGION_FILTER,
    ID_GLOBAL_RESET_BTN,
    ID_GLOBAL_CHIPS,
    GLOBAL_FILTER_DEFAULTS,
    USER_FILTER_LABELS,
    REGION_FILTER_LABELS,
)

logger = logging.getLogger(__name__)


def _timeframe_chip(value: str) -> html.Span | None:
    if value in ("All", None):
        return None
    label = "Weekdays Only" if value == "Weekday" else "Weekends Only"
    return html.Span(
        className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border bg-amber-50 border-amber-200 text-amber-700",
        children=[
            html.I(className="fas fa-calendar-alt text-[9px]"),
            label,
        ],
    )


def _user_chip(value: str) -> html.Span | None:
    if value in ("All", None):
        return None
    label = USER_FILTER_LABELS.get(value, value)
    return html.Span(
        className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border bg-teal-50 border-teal-200 text-teal-700",
        children=[
            html.I(className="fas fa-user text-[9px]"),
            label,
        ],
    )


def _region_chip(value: str) -> html.Span | None:
    if value in ("All", None):
        return None
    label = REGION_FILTER_LABELS.get(value, value)
    return html.Span(
        className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border bg-blue-50 border-blue-200 text-blue-700",
        children=[
            html.I(className="fas fa-map-marker-alt text-[9px]"),
            label,
        ],
    )


def _build_chips(timeframe: str, user: str, region: str) -> list:
    chips = []
    t = _timeframe_chip(timeframe)
    u = _user_chip(user)
    r = _region_chip(region)
    if t:
        chips.append(t)
    if u:
        chips.append(u)
    if r:
        chips.append(r)
    if not chips:
        chips.append(
            html.Span("All Data View Active", className="text-[11px] text-slate-400 italic")
        )
    return chips


def register_global_filter_callbacks(app) -> None:
    """Attach global-filter callbacks to the Dash app instance."""

    # 1. Reset button -> restore all dropdowns to default
    @app.callback(
        Output(ID_GLOBAL_TIMEFRAME,     "value"),
        Output(ID_GLOBAL_USER_FILTER,   "value"),
        Output(ID_GLOBAL_REGION_FILTER, "value"),
        Input(ID_GLOBAL_RESET_BTN, "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(_n):
        return (
            GLOBAL_FILTER_DEFAULTS["timeframe"],
            GLOBAL_FILTER_DEFAULTS["user_type"],
            GLOBAL_FILTER_DEFAULTS["region"],
        )

    # 2. Dropdowns -> Store dict
    @app.callback(
        Output(ID_GLOBAL_STORE, "data"),
        Input(ID_GLOBAL_TIMEFRAME,     "value"),
        Input(ID_GLOBAL_USER_FILTER,   "value"),
        Input(ID_GLOBAL_REGION_FILTER, "value"),
    )
    def update_store(timeframe: str, user_type: str, region: str) -> dict:
        return {
            "timeframe": timeframe or GLOBAL_FILTER_DEFAULTS["timeframe"],
            "user_type": user_type or GLOBAL_FILTER_DEFAULTS["user_type"],
            "region":    region    or GLOBAL_FILTER_DEFAULTS["region"],
        }

    # 3. Store -> Active Chips row
    @app.callback(
        Output(ID_GLOBAL_CHIPS, "children"),
        Input(ID_GLOBAL_STORE,  "data"),
    )
    def render_chips(data: dict | None) -> list:
        if not data:
            return _build_chips("All", "All", "All")
        return _build_chips(
            data.get("timeframe", "All"),
            data.get("user_type", "All"),
            data.get("region", "All"),
        )
