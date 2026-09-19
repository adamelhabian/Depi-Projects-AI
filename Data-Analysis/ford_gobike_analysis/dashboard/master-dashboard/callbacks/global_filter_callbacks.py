"""
callbacks/global_filter_callbacks.py – Global Filter State Controller
======================================================================
Manages the master-global-filter-store (dcc.Store) and the associated UI:
  1. Store Update: Syncs Membership + Region dropdowns → Store dict
  2. Reset Button: Clears both dropdowns back to "All" when user clicks Reset
  3. Chip Renderer: Draws active-filter pills from Store values

Station (M-5) and Time-User (M-4) modules listen to this Store as State
inside their own page-level callbacks (see pages/station_page.py and
pages/time_user_page.py).
"""

from __future__ import annotations

import logging
from dash import Input, Output, State, html, callback_context, no_update

from config import (
    ID_GLOBAL_STORE,
    ID_GLOBAL_USER_FILTER,
    ID_GLOBAL_REGION_FILTER,
    ID_GLOBAL_RESET_BTN,
    ID_GLOBAL_CHIPS,
    GLOBAL_FILTER_DEFAULTS,
    USER_FILTER_LABELS,
    REGION_FILTER_LABELS,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Chip builder helpers
# ---------------------------------------------------------------------------

def _user_chip(value: str) -> html.Span | None:
    """Return a rider-type chip, or None when the value is the default."""
    if value == "All":
        return None
    label = USER_FILTER_LABELS.get(value, value)
    return html.Span(
        className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border bg-indigo-50 border-indigo-200 text-indigo-700",
        children=[
            html.I(className="fas fa-user text-[9px]"),
            label,
        ],
    )


def _region_chip(value: str) -> html.Span | None:
    """Return a region chip, or None when the value is the default."""
    if value == "All":
        return None
    label = REGION_FILTER_LABELS.get(value, value)
    return html.Span(
        className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border bg-emerald-50 border-emerald-200 text-emerald-700",
        children=[
            html.I(className="fas fa-map-marker-alt text-[9px]"),
            label,
        ],
    )


def _build_chips(user: str, region: str) -> list:
    """Assemble the chip list. Falls back to a quiet 'All Active' label."""
    chips = []
    u = _user_chip(user)
    r = _region_chip(region)
    if u:
        chips.append(u)
    if r:
        chips.append(r)
    if not chips:
        chips.append(
            html.Span("All filters active", className="text-[11px] text-slate-400 italic")
        )
    return chips


# ---------------------------------------------------------------------------
# Callback registration
# ---------------------------------------------------------------------------

def register_global_filter_callbacks(app) -> None:
    """Attach global-filter callbacks to the Dash app instance."""

    # 1. Reset button → restore both dropdowns to default ──────────────────
    @app.callback(
        Output(ID_GLOBAL_USER_FILTER,   "value"),
        Output(ID_GLOBAL_REGION_FILTER, "value"),
        Input(ID_GLOBAL_RESET_BTN, "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(_n):
        """Return both dropdowns to default values on Reset click."""
        return GLOBAL_FILTER_DEFAULTS["user_type"], GLOBAL_FILTER_DEFAULTS["region"]

    # 2. Dropdowns → Store dict ─────────────────────────────────────────────
    @app.callback(
        Output(ID_GLOBAL_STORE, "data"),
        Input(ID_GLOBAL_USER_FILTER,   "value"),
        Input(ID_GLOBAL_REGION_FILTER, "value"),
    )
    def update_store(user_type: str, region: str) -> dict:
        """Write current dropdown values into the session Store."""
        return {
            "user_type": user_type or GLOBAL_FILTER_DEFAULTS["user_type"],
            "region":    region    or GLOBAL_FILTER_DEFAULTS["region"],
        }

    # 3. Store → Active Chips row ───────────────────────────────────────────
    @app.callback(
        Output(ID_GLOBAL_CHIPS, "children"),
        Input(ID_GLOBAL_STORE,  "data"),
    )
    def render_chips(data: dict | None) -> list:
        """Re-render the active-filter chip pills whenever the store changes."""
        if not data:
            return _build_chips("All", "All")
        return _build_chips(
            data.get("user_type", "All"),
            data.get("region",    "All"),
        )
