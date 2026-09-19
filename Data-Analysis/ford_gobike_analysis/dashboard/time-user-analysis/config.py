"""
config.py – Central Configuration for the Dashboard
====================================================
Single source of truth for every shared constant:

  - Path resolution (DATA_PATH / project root)
  - Component IDs (used by layout.py and callbacks)
  - Filter defaults (Top-N slider bounds, etc.)
  - Color palette (Tailwind-inspired)
  - Font family
  - Map tile style, region presets, and map center/zoom
  - Coordinate validation ranges
  - Required and coordinate column names
  - Chart heights (one per chart family)
  - Sidebar navigation constants (unique Desktop + Mobile IDs)

This module must remain dependency-free (only stdlib) so that any other
module can import from it without circular-import risk.
"""

from __future__ import annotations

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Path Resolution & Data Location
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent

DATA_PATH = os.environ.get(
    "DASHBOARD_DATA_PATH",
    str(PROJECT_ROOT / "data"),
)


# ---------------------------------------------------------------------------
# Component IDs
# ---------------------------------------------------------------------------
# Map & charts
ID_MAP                     = "m5-map"
ID_TOP_STATIONS            = "m5-top-stations"
ID_TOP_ROUTES              = "m5-top-routes"
ID_FLOW_IMBALANCE          = "m5-flow-imbalance"
ID_ROUND_TRIP_CHART        = "m5-round-trip-chart"

# Time Analysis charts (Phase 1)
ID_TRIPS_BY_HOUR           = "m5-trips-by-hour"
ID_DAY_HOUR_HEATMAP        = "m5-day-hour-heatmap"
ID_AVG_DURATION_BY_HOUR    = "m5-avg-duration-by-hour"
ID_WEEKDAY_WEEKEND_DURATION = "m5-weekday-weekend-duration"

# User Analysis charts (Phase 2)
ID_USER_TYPE_DISTRIBUTION   = "m5-user-type-distribution"
ID_USER_TYPE_HOUR           = "m5-user-type-hour"
ID_AVG_DURATION_BY_USER_TYPE = "m5-avg-duration-by-user-type"
ID_AGE_GROUP_DISTRIBUTION   = "m5-age-group-distribution"
ID_GENDER_DISTRIBUTION      = "m5-gender-distribution"
ID_USER_TYPE_BY_AGE_GROUP   = "m5-user-type-by-age-group"

# Containers & stores
ID_INSPECTOR_CONTAINER     = "m5-inspector-container"
ID_DISPATCH_CONTAINER      = "m5-dispatch-container"
ID_SELECTED_STATION_STORE  = "m5-selected-station-store"

# Filters & controls
ID_USER_FILTER             = "m5-user-filter"
ID_TOP_N_SLIDER            = "m5-top-n-slider"
ID_REGION_FILTER           = "m5-region-filter"
ID_MAP_FLOW_LINES_TOGGLE   = "m5-map-flow-lines-toggle"

# Downloads & drawer actions
ID_DOWNLOAD_BTN            = "m5-download-btn"
ID_DOWNLOAD_DATA           = "m5-download-data"
ID_DRAWER_CLOSE_BTN        = "m5-drawer-close-btn"
ID_DRAWER_FOCUS_BTN        = "m5-drawer-focus-btn"

# ---------------------------------------------------------------------------
# Sidebar Navigation (Phase 1 – Sidebar Foundation)
# ---------------------------------------------------------------------------
# Global navigation state
ID_ACTIVE_SECTION_STORE    = "m5-active-section-store"
ID_ACTIVE_ANCHOR_STORE     = "m5-active-anchor-store"
ID_MOBILE_MENU_STORE       = "m5-mobile-menu-store"

# Sidebar shells
ID_SIDEBAR_CONTAINER       = "m5-sidebar-desktop"
ID_MOBILE_SIDEBAR          = "m5-sidebar-mobile"
ID_MOBILE_MENU_TOGGLE      = "m5-mobile-menu-toggle"
ID_MOBILE_BACKDROP         = "m5-mobile-backdrop"

# Section wrapper IDs
ID_SECTION_STATION         = "m5-section-station"
ID_SECTION_TIME            = "m5-section-time"
ID_SECTION_USER            = "m5-section-user"
ID_SECTION_DISPATCH        = "m5-section-dispatch"

# Filter panel wrapper (hidden outside Station Analysis)
ID_FILTER_PANEL_WRAPPER    = "m5-filter-panel-wrapper"

# --- Desktop navigation controls -------------------------------------------
ID_NAV_STATION_DESKTOP     = "m5-nav-station-desktop"
ID_NAV_TIME_DESKTOP        = "m5-nav-time-desktop"
ID_NAV_USER_DESKTOP        = "m5-nav-user-desktop"
ID_NAV_DISPATCH_DESKTOP    = "m5-nav-dispatch-desktop"

ID_ANCHOR_STATION_NETWORK_DESKTOP = "m5-anchor-station-network-desktop"
ID_ANCHOR_STATION_TRAFFIC_DESKTOP = "m5-anchor-station-traffic-desktop"
ID_ANCHOR_STATION_FLOW_DESKTOP    = "m5-anchor-station-flow-desktop"

ID_ANCHOR_TIME_HOURLY_DESKTOP   = "m5-anchor-time-hourly-desktop"
ID_ANCHOR_TIME_DAYHOUR_DESKTOP  = "m5-anchor-time-dayhour-desktop"
ID_ANCHOR_TIME_DURATION_DESKTOP = "m5-anchor-time-duration-desktop"

ID_ANCHOR_USER_TYPE_DESKTOP     = "m5-anchor-user-type-desktop"
ID_ANCHOR_USER_DEMO_DESKTOP     = "m5-anchor-user-demographics-desktop"
ID_ANCHOR_USER_CROSSTAB_DESKTOP = "m5-anchor-user-crosstab-desktop"

ID_ANCHOR_DISPATCH_PLAN_DESKTOP = "m5-anchor-dispatch-plan-desktop"

# --- Mobile navigation controls --------------------------------------------
ID_NAV_STATION_MOBILE      = "m5-nav-station-mobile"
ID_NAV_TIME_MOBILE         = "m5-nav-time-mobile"
ID_NAV_USER_MOBILE         = "m5-nav-user-mobile"
ID_NAV_DISPATCH_MOBILE     = "m5-nav-dispatch-mobile"

ID_ANCHOR_STATION_NETWORK_MOBILE = "m5-anchor-station-network-mobile"
ID_ANCHOR_STATION_TRAFFIC_MOBILE = "m5-anchor-station-traffic-mobile"
ID_ANCHOR_STATION_FLOW_MOBILE    = "m5-anchor-station-flow-mobile"

ID_ANCHOR_TIME_HOURLY_MOBILE   = "m5-anchor-time-hourly-mobile"
ID_ANCHOR_TIME_DAYHOUR_MOBILE  = "m5-anchor-time-dayhour-mobile"
ID_ANCHOR_TIME_DURATION_MOBILE = "m5-anchor-time-duration-mobile"

ID_ANCHOR_USER_TYPE_MOBILE     = "m5-anchor-user-type-mobile"
ID_ANCHOR_USER_DEMO_MOBILE     = "m5-anchor-user-demographics-mobile"
ID_ANCHOR_USER_CROSSTAB_MOBILE = "m5-anchor-user-crosstab-mobile"

ID_ANCHOR_DISPATCH_PLAN_MOBILE = "m5-anchor-dispatch-plan-mobile"

# Section keys
SECTION_KEY_STATION        = "station"
SECTION_KEY_TIME           = "time"
SECTION_KEY_USER           = "user"
SECTION_KEY_DISPATCH       = "dispatch"
DEFAULT_ACTIVE_SECTION     = SECTION_KEY_STATION


# ---------------------------------------------------------------------------
# Filter Defaults (Top-N Slider & related)
# ---------------------------------------------------------------------------
DEFAULT_TOP_N  = 10
TOP_N_MIN      = 1
TOP_N_MAX      = 30
TOP_N_STEP     = 1


# ---------------------------------------------------------------------------
# Color Palette (Tailwind-inspired)
# ---------------------------------------------------------------------------
COLORS = {
    "bg_card":       "#ffffff",
    "bg_surface":    "#f8fafc",
    "text_main":     "#0f172a",
    "text_muted":    "#64748b",
    "accent_teal":   "#0d9488",
    "accent_purple": "#a855f7",
    "accent_dim":    "#94a3b8",
    "success":       "#10b981",
    "danger":        "#f43f5e",
    "warning":       "#f59e0b",
    "border":        "#e2e8f0",
}


# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


# ---------------------------------------------------------------------------
# Map Configuration
# ---------------------------------------------------------------------------
MAP_TILE_STYLE = "carto-positron"

MAP_CENTER = {"lat": 37.7749, "lon": -122.4194}
MAP_ZOOM   = 11

REGIONS = {
    "All": {
        "center": {"lat": 37.7749, "lon": -122.4194},
        "zoom":   11,
    },
    "San Francisco": {
        "center": {"lat": 37.7749, "lon": -122.4194},
        "zoom":   12.5,
    },
    "East Bay": {
        "center": {"lat": 37.8044, "lon": -122.2712},
        "zoom":   12,
    },
    "San Jose": {
        "center": {"lat": 37.3382, "lon": -121.8863},
        "zoom":   12,
    },
}


# ---------------------------------------------------------------------------
# Coordinate Validation Ranges (Bay Area bounding box)
# ---------------------------------------------------------------------------
VALID_LAT_RANGE = (37.0, 38.5)
VALID_LON_RANGE = (-123.0, -121.5)


# ---------------------------------------------------------------------------
# Column Name Contracts
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = [
    "start_station_name",
    "end_station_name",
    "start_station_latitude",
    "start_station_longitude",
    "end_station_latitude",
    "end_station_longitude",
    "duration_min",
    "user_type",
]

COORDINATE_COLUMNS = [
    "start_station_latitude",
    "start_station_longitude",
    "end_station_latitude",
    "end_station_longitude",
]


# ---------------------------------------------------------------------------
# Chart Heights
# ---------------------------------------------------------------------------
CHART_HEIGHT_MAP        = 520
CHART_HEIGHT_BAR        = 380
CHART_HEIGHT_IMBALANCE  = 380
CHART_HEIGHT_LEISURE    = 380

# Time Analysis (added in Phase 1)
CHART_HEIGHT_LINE       = 320
CHART_HEIGHT_HEATMAP    = 380