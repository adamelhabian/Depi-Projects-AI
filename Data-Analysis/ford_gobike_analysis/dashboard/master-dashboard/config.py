"""
config.py – Master Dashboard Central Configuration
===================================================
Ford GoBike Master Analytics Platform
Central configuration for routing, theme colors, navigation items, and component IDs.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Path Resolution
# ---------------------------------------------------------------------------
CURRENT_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = CURRENT_DIR.parent
STATION_MODULE_DIR = DASHBOARD_DIR / "station-trip-analysis"
TIME_USER_MODULE_DIR = DASHBOARD_DIR / "time-user-analysis"

# ---------------------------------------------------------------------------
# 2. Application Server Configuration
# ---------------------------------------------------------------------------
APP_TITLE = "Ford GoBike | Master Analytics Platform"
APP_PORT = int(os.environ.get("PORT", 8050))
APP_HOST = os.environ.get("HOST", "127.0.0.1")
DEBUG_MODE = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

# ---------------------------------------------------------------------------
# 3. Route Definitions & Navigation Items
# ---------------------------------------------------------------------------
ROUTE_OVERVIEW = "/"
ROUTE_STATIONS = "/stations"
ROUTE_TIME_USER = "/time-user"
ROUTE_USER_TRIPS = "/user-trips"

NAV_ITEMS = [
    {
        "id": "nav-overview",
        "route": ROUTE_OVERVIEW,
        "label": "Executive Overview",
        "icon": "fas fa-chart-pie",
        "badge": "Overview",
        "badge_color": "bg-indigo-900/60 text-indigo-300",
        "description": "Cross-cutting fleet insights, summary metrics & status",
    },
    {
        "id": "nav-stations",
        "route": ROUTE_STATIONS,
        "label": "Station & Network Flow",
        "icon": "fas fa-map-marked-alt",
        "badge": "Flow",
        "badge_color": "bg-emerald-900/60 text-emerald-300",
        "description": "Geospatial traffic, top corridors & network imbalance",
    },
    {
        "id": "nav-time-user",
        "route": ROUTE_TIME_USER,
        "label": "Time & Rider Demographics",
        "icon": "fas fa-user-clock",
        "badge": "Demographics",
        "badge_color": "bg-teal-900/60 text-teal-300",
        "description": "Commuter rhythms, hourly demand & demographic splits",
    },
    {
        "id": "nav-user-trips",
        "route": ROUTE_USER_TRIPS,
        "label": "Rider & Trip Dynamics",
        "icon": "fas fa-users-cog",
        "badge": "Cohorts",
        "badge_color": "bg-purple-900/60 text-purple-300",
        "description": "Rider cohorts, gender behaviors, duration profiles & user trip velocity",
    },
]

# ---------------------------------------------------------------------------
# 4. Master Component IDs
# ---------------------------------------------------------------------------
ID_URL = "master-url"
ID_PAGE_CONTENT = "master-page-content"
ID_SIDEBAR = "master-sidebar"
ID_SIDEBAR_TOGGLE = "master-sidebar-toggle"
ID_DB_STATUS = "master-db-status"
ID_NAV_CONTAINER = "master-nav-container"

# Overview Page IDs
ID_OVERVIEW_TRIPS_METRIC     = "master-overview-trips"
ID_OVERVIEW_STATIONS_METRIC  = "master-overview-stations"
ID_OVERVIEW_SUBSCRIBER_METRIC= "master-overview-subscribers"
ID_OVERVIEW_DURATION_METRIC  = "master-overview-duration"
ID_OVERVIEW_RECENT_CHART     = "master-overview-recent-chart"

# Export Component IDs
ID_GLOBAL_EXPORT_BTN         = "global-export-btn"
ID_GLOBAL_DOWNLOAD_EXPORT    = "global-export-download"

# ---------------------------------------------------------------------------
# 5. Global Filter Bar IDs (shared across all pages via dcc.Store)
# ---------------------------------------------------------------------------
ID_GLOBAL_STORE        = "master-global-filter-store"   # dcc.Store holds the dict
ID_GLOBAL_USER_FILTER  = "master-global-user-filter"    # Dropdown: Rider Type
ID_GLOBAL_REGION_FILTER= "master-global-region-filter"  # Dropdown: Region
ID_GLOBAL_GENDER_FILTER= "master-global-gender-filter"  # Dropdown: Gender (New Filter 1)
ID_GLOBAL_DAY_FILTER   = "master-global-day-filter"     # Dropdown: Day Type (New Filter 2)
ID_GLOBAL_RESET_BTN    = "master-global-reset-btn"      # Reset button
ID_GLOBAL_CHIPS        = "master-global-active-chips"   # Active filter chips row

# Default values written to the Store on initial load
GLOBAL_FILTER_DEFAULTS = {
    "user_type": "All",
    "region": "All",
    "gender": "All",
    "day_type": "All",
    "timeframe": "all",
}

# Human-readable labels for the chips
USER_FILTER_LABELS = {
    "All":        "All Riders",
    "Subscriber": "Subscribers",
    "Customer":   "Casual",
}
REGION_FILTER_LABELS = {
    "All":                        "All Bay Area",
    "San Francisco":              "San Francisco",
    "East Bay (Oakland/Berkeley)":"East Bay",
    "San Jose":                   "San Jose",
}
GENDER_FILTER_LABELS = {
    "All":    "All Genders",
    "Male":   "Male",
    "Female": "Female",
    "Other":  "Other",
}
DAY_FILTER_LABELS = {
    "All":     "All Days",
    "Weekday": "Weekdays",
    "Weekend": "Weekends",
}

# ---------------------------------------------------------------------------
# 5. Theme Palette (Modern Executive BI Theme)
# ---------------------------------------------------------------------------
COLORS = {
    "bg_body": "#F8FAFC",
    "bg_sidebar": "#0F172A",
    "bg_card": "#FFFFFF",
    "border": "#E2E8F0",
    "border_sidebar": "#1E293B",
    "text_primary": "#0F172A",
    "text_secondary": "#64748B",
    "text_light": "#94A3B8",
    "text_sidebar": "#E2E8F0",
    "text_sidebar_muted": "#64748B",
    "accent_emerald": "#10B981",
    "accent_teal": "#0D9488",
    "accent_indigo": "#6366F1",
    "accent_purple": "#A855F7",
}

FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
