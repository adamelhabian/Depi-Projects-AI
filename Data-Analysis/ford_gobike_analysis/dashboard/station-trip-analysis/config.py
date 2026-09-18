"""
config.py – Member 5: Station & Trip Analysis Configuration
=============================================================
Centralized configuration, color palette, directory paths, and region presets.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Path Resolution
# ---------------------------------------------------------------------------
_CURRENT_DIR = Path(__file__).resolve().parent
CSV_FILENAME = os.environ.get("GOBIKE_CSV", "cleaned_fordgobike_master.csv")

# Candidate search locations for the dataset
_SEARCH_PATHS = [
    Path(os.environ.get("GOBIKE_DATA_DIR", "")) / CSV_FILENAME if os.environ.get("GOBIKE_DATA_DIR") else None,
    _CURRENT_DIR / CSV_FILENAME,
    _CURRENT_DIR.parent / CSV_FILENAME,
    _CURRENT_DIR.parent.parent / CSV_FILENAME,
    _CURRENT_DIR.parent.parent.parent / CSV_FILENAME,
    Path("d:/Depi R5/DA Final Project/Phase 2") / CSV_FILENAME,
]

DATA_PATH = next((p for p in _SEARCH_PATHS if p and p.exists()), _CURRENT_DIR / CSV_FILENAME)

# ---------------------------------------------------------------------------
# 2. Central Color Palette (Clean Mint / Emerald / Lime Theme)
# ---------------------------------------------------------------------------
COLORS = {
    "bg_primary": "#F8FAFC",
    "bg_secondary": "#FFFFFF",
    "bg_card": "#FFFFFF",
    "bg_card_hover": "#FFFFFF",
    "border": "#E2E8F0",
    "border_focus": "#10B981",
    "accent": "#10B981",
    "accent_dim": "#059669",
    "accent_lime": "#84CC16",
    "accent_teal": "#0D9488",
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#F43F5E",
}

FONT_FAMILY = "'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

# ---------------------------------------------------------------------------
# 3. Chart Layout & Dimension Defaults
# ---------------------------------------------------------------------------
CHART_HEIGHT_MAP = 500
CHART_HEIGHT_BAR = 380
CHART_HEIGHT_IMBALANCE = 380
CHART_HEIGHT_LEISURE = 380

# ---------------------------------------------------------------------------
# 4. Regional Map Settings & Boundaries
# ---------------------------------------------------------------------------
MAP_TILE_STYLE = "carto-positron"

REGIONS = {
    "All": {
        "name": "All Bay Area",
        "center": {"lat": 37.776, "lon": -122.416},
        "zoom": 10.8,
    },
    "San Francisco": {
        "name": "San Francisco",
        "center": {"lat": 37.774, "lon": -122.419},
        "zoom": 12.3,
    },
    "East Bay (Oakland/Berkeley)": {
        "name": "East Bay (Oakland/Berkeley)",
        "center": {"lat": 37.820, "lon": -122.260},
        "zoom": 12.0,
    },
    "San Jose": {
        "name": "San Jose",
        "center": {"lat": 37.335, "lon": -121.890},
        "zoom": 13.0,
    },
}

MAP_CENTER = REGIONS["All"]["center"]
MAP_ZOOM = REGIONS["All"]["zoom"]

VALID_LAT_RANGE = (36.5, 38.5)
VALID_LON_RANGE = (-123.0, -121.5)

# ---------------------------------------------------------------------------
# 5. Schema Requirements
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = {
    "start_station_name",
    "end_station_name",
}

COORDINATE_COLUMNS = {
    "start_station_latitude",
    "start_station_longitude",
    "end_station_latitude",
    "end_station_longitude",
}

# ---------------------------------------------------------------------------
# 6. Filter Defaults
# ---------------------------------------------------------------------------
DEFAULT_TOP_N = 10
TOP_N_MIN = 5
TOP_N_MAX = 20
TOP_N_STEP = 5

# ---------------------------------------------------------------------------
# 7. Component IDs
# ---------------------------------------------------------------------------
ID_USER_FILTER = "m5-user-filter"
ID_TOP_N_SLIDER = "m5-top-n-slider"
ID_REGION_FILTER = "m5-region-filter"
ID_MAP_FLOW_LINES_TOGGLE = "m5-map-flow-lines"
ID_DOWNLOAD_BTN = "m5-download-btn"
ID_DOWNLOAD_DATA = "m5-download-data"

ID_MAP = "m5-station-map"
ID_TOP_STATIONS = "m5-top-stations-chart"
ID_TOP_ROUTES = "m5-top-routes-chart"
ID_FLOW_IMBALANCE = "m5-flow-imbalance-chart"
ID_ROUND_TRIP_CHART = "m5-round-trip-chart"

ID_INSPECTOR_CONTAINER = "m5-inspector-container"
ID_DISPATCH_CONTAINER = "m5-dispatch-container"
ID_SELECTED_STATION_STORE = "m5-selected-station-store"
ID_DRAWER_CLOSE_BTN = "m5-drawer-close-btn"
ID_DRAWER_FOCUS_BTN = "m5-drawer-focus-btn"
