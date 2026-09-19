"""
callbacks/global_filter_sync.py – Global→Local Filter Bridge
=============================================================
Bridges the master `dcc.Store` global filter values into the local
filter dropdowns of each sub-module (station M-5 and time-user M-4).

How it works:
  - Listens to ID_GLOBAL_STORE changes
  - Writes the values directly into the sub-module dropdowns
    (m5-user-filter, m5-region-filter, tu-user-filter, tu-day-filter)
  - Each sub-module's OWN callbacks still fire normally via those dropdowns

This means the global filter bar controls both dashboards simultaneously
without needing to touch the sub-modules' internal callback code.
"""

from __future__ import annotations

import logging
from dash import Input, Output, State

from config import ID_GLOBAL_STORE, GLOBAL_FILTER_DEFAULTS

logger = logging.getLogger(__name__)

# Sub-module filter component IDs (from their respective config.py files)
# Station (M-5) uses m5-* prefix
_M5_USER_FILTER   = "m5-user-filter"
_M5_REGION_FILTER = "m5-region-filter"

# Time-User (M-4) uses tu-* prefix
_TU_USER_FILTER   = "tu-user-filter"
# M-4 has a day filter but NOT a region filter — we skip region for M-4


def register_global_filter_sync_callbacks(app) -> None:
    """
    Register bridge callbacks that push Store values into sub-module dropdowns.
    suppress_callback_exceptions=True must be set on the app (already is).
    """

    # ── Bridge: Store → Station (M-5) user + region filters ────────────────
    @app.callback(
        Output(_M5_USER_FILTER,   "value"),
        Output(_M5_REGION_FILTER, "value"),
        Input(ID_GLOBAL_STORE,    "data"),
    )
    def sync_to_station_filters(data: dict | None):
        """Push global filter values into the station module dropdowns."""
        if not data:
            return (
                GLOBAL_FILTER_DEFAULTS["user_type"],
                GLOBAL_FILTER_DEFAULTS["region"],
            )
        return (
            data.get("user_type", GLOBAL_FILTER_DEFAULTS["user_type"]),
            data.get("region",    GLOBAL_FILTER_DEFAULTS["region"]),
        )

    # ── Bridge: Store → Time-User (M-4) user filter ────────────────────────
    @app.callback(
        Output(_TU_USER_FILTER, "value"),
        Input(ID_GLOBAL_STORE,  "data"),
    )
    def sync_to_time_user_filters(data: dict | None):
        """Push global user-type value into the time-user module dropdown."""
        if not data:
            return GLOBAL_FILTER_DEFAULTS["user_type"]
        return data.get("user_type", GLOBAL_FILTER_DEFAULTS["user_type"])
