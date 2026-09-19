"""
config.py – Central Configuration for Time & User Analysis Dashboard
====================================================================
Member 4 Section · Collaborative Ford GoBike Analytics Project

Defines component IDs, theme colors, typography, and chart layout constants.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Path Resolution
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Component IDs
# ---------------------------------------------------------------------------
# KPI Cards
ID_KPI_TOTAL_TRIPS        = "tu-kpi-total-trips"
ID_KPI_SUBSCRIBER_PCT     = "tu-kpi-subscriber-pct"
ID_KPI_PEAK_HOUR          = "tu-kpi-peak-hour"
ID_KPI_AVG_DURATION       = "tu-kpi-avg-duration"

# Filter Controls
ID_USER_FILTER            = "tu-user-filter"
ID_DAY_FILTER             = "tu-day-filter"

# Core Visualizations (5 Core Charts)
ID_TRIPS_BY_HOUR          = "tu-trips-by-hour"
ID_TRIPS_BY_DAY           = "tu-trips-by-day"
ID_USER_TYPE_DISTRIBUTION = "tu-user-type-distribution"
ID_USER_TYPE_HOUR         = "tu-user-type-hour"
ID_AGE_GROUP_DISTRIBUTION = "tu-age-group-distribution"

# ---------------------------------------------------------------------------
# Color Palette (Tailwind & Plotly BI-Grade Theme)
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
# Typography & Chart Heights
# ---------------------------------------------------------------------------
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

CHART_HEIGHT_LINE    = 340
CHART_HEIGHT_HEATMAP = 340
CHART_HEIGHT_BAR     = 340

# ---------------------------------------------------------------------------
# Analytical Schema Contract
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = [
    "hour",
    "day_of_week",
    "duration_min",
    "user_type",
    "member_age",
]