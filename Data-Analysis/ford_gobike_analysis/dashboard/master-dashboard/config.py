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

NAV_ITEMS = [
    {
        "id": "nav-overview",
        "route": ROUTE_OVERVIEW,
        "label": "Executive Overview",
        "icon": "fas fa-chart-pie",
        "badge": "Overview",
        "badge_color": "bg-teal-500/10 text-teal-400 border border-teal-500/20",
        "description": "Cross-cutting fleet insights, summary metrics & status",
    },
    {
        "id": "nav-stations",
        "route": ROUTE_STATIONS,
        "label": "Station & Network Flow",
        "icon": "fas fa-map-marked-alt",
        "badge": "M-5",
        "badge_color": "bg-blue-500/10 text-blue-400 border border-blue-500/20",
        "description": "Geospatial traffic, top corridors & network imbalance",
    },
    {
        "id": "nav-time-user",
        "route": ROUTE_TIME_USER,
        "label": "Time & Rider Demographics",
        "icon": "fas fa-user-clock",
        "badge": "M-4",
        "badge_color": "bg-purple-500/10 text-purple-400 border border-purple-500/20",
        "description": "Commuter rhythms, hourly demand & demographic splits",
    },
]

# ---------------------------------------------------------------------------
# 4. Master Shell Component IDs
# ---------------------------------------------------------------------------
ID_URL = "master-url"
ID_PAGE_CONTENT = "master-page-content"
ID_SIDEBAR = "master-sidebar"
ID_SIDEBAR_TOGGLE = "master-sidebar-toggle"
ID_DB_STATUS = "master-db-status"
ID_NAV_CONTAINER = "master-nav-container"

# ---------------------------------------------------------------------------
# 5. Global Filter Bar IDs (shared across all pages via dcc.Store)
# ---------------------------------------------------------------------------
ID_GLOBAL_STORE         = "master-global-filters"        # dcc.Store(id="master-global-filters", storage_type="session")
ID_GLOBAL_TIMEFRAME     = "master-global-timeframe"      # Dropdown/segmented: All, Weekday, Weekend
ID_GLOBAL_USER_FILTER   = "master-global-user-filter"    # Dropdown: All, Subscriber, Customer
ID_GLOBAL_REGION_FILTER = "master-global-region-filter"  # Dropdown: All, San Francisco, East Bay, San Jose
ID_GLOBAL_RESET_BTN     = "master-global-reset-btn"      # Reset button
ID_GLOBAL_CHIPS         = "master-global-active-chips"   # Active filter chips row

# Default values written to the Store on initial load
GLOBAL_FILTER_DEFAULTS = {
    "timeframe": "All",
    "user_type": "All",
    "region": "All",
}

USER_FILTER_LABELS = {
    "All": "All Riders",
    "Subscriber": "Subscribers",
    "Customer": "Casual Customers",
}

REGION_FILTER_LABELS = {
    "All": "All Bay Area",
    "San Francisco": "San Francisco",
    "East Bay": "East Bay",
    "San Jose": "San Jose",
}

# ---------------------------------------------------------------------------
# 6. Page 1: Executive Overview IDs
# ---------------------------------------------------------------------------
ID_OVERVIEW_DEMAND_CHART  = "master-overview-demand-chart"
ID_OVERVIEW_STATION_MAP   = "master-overview-station-map"
ID_OVERVIEW_INSIGHTS_GRID = "master-overview-insights-grid"

# ---------------------------------------------------------------------------
# 7. Page 2: Station & Network Flow IDs
# ---------------------------------------------------------------------------
ID_STATION_TOPN_SLIDER              = "station-topn-slider"
ID_STATION_CORRIDOR_TOGGLE          = "station-corridor-toggle"
ID_STATION_MAP                      = "station-map-graph"
ID_STATION_DRAWER                   = "station-profile-drawer"
ID_STATION_DRAWER_CONTENT           = "station-drawer-content"
ID_STATION_DRAWER_CLOSE             = "station-drawer-close-btn"
ID_STATION_CHART_BUSIEST            = "station-chart-busiest"
ID_STATION_CHART_DEFICIT            = "station-chart-deficit"
ID_STATION_CHART_SURPLUS            = "station-chart-surplus"
ID_STATION_CHART_LOOPS              = "station-chart-loops"
ID_STATION_REBALANCING_CONTAINER    = "station-rebalancing-grid"
ID_STATION_REBALANCING_DOWNLOAD_BTN = "station-rebalance-download-btn"
ID_STATION_REBALANCING_DOWNLOAD     = "station-rebalance-download"

# ---------------------------------------------------------------------------
# 8. Page 3: Time & User Demographics IDs
# ---------------------------------------------------------------------------
ID_TU_HOURLY_CHART   = "tu-hourly-demand-chart"
ID_TU_DOW_CHART      = "tu-dow-volume-chart"
ID_TU_HEATMAP        = "tu-heatmap-matrix"
ID_TU_DONUT          = "tu-user-split-donut"
ID_TU_AGE_CHART      = "tu-age-cohort-chart"
ID_TU_DURATION_HIST  = "tu-duration-hist-chart"

# ---------------------------------------------------------------------------
# 9. Design Tokens & Semantic Color Palette
# ---------------------------------------------------------------------------
COLORS = {
    # Surfaces & Borders
    "brand_dark": "#0B1329",
    "card_bg": "#FFFFFF",
    "body_bg": "#F8FAFC",
    "border": "#E2E8F0",
    "text_main": "#0F172A",
    "text_muted": "#64748B",
    "text_subtle": "#94A3B8",

    # Semantic Status Roles
    "subscriber": "#14B8A6",       # Primary Teal (Subscribers, 90.5%)
    "customer": "#A855F7",         # Purple (Casual Customers, 9.5%)
    "deficit": "#F97316",          # Orange/Coral (Net Deficit / Outbound > Inbound)
    "surplus": "#3B82F6",          # Blue (Net Surplus / Inbound > Outbound)
    "balanced": "#94A3B8",         # Slate (Balanced flow)
}

FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

