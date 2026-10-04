"""
callbacks/overview_callbacks.py – Reactive Controller for Executive Overview
=============================================================================
Connects the global filter store (master-global-filter-store) to the
Executive Overview page:
  1. Updates the 6 KPI cards with live values and sparklines
  2. Updates the Computed System Insights panel
  3. Updates the Daily Ridership & Prior Period Benchmark area line chart
"""

from __future__ import annotations

import logging
from dash import Input, Output, no_update
import dash

from config import ID_GLOBAL_STORE
from components.kpi_banner import render_kpi_banner
from components.key_insights import render_key_insights
from components.overview_charts import create_overview_daily_trend_chart
from data_loader import (
    get_filtered_overview_kpis,
    get_filtered_overview_daily,
)

logger = logging.getLogger(__name__)


def register_overview_callbacks(app: dash.Dash) -> None:
    """Register reactive overview filtering callbacks."""

    @app.callback(
        [
            Output("overview-kpi-banner-container", "children"),
            Output("overview-insights-container", "children"),
            Output("overview-trend-graph", "figure"),
        ],
        Input(ID_GLOBAL_STORE, "data"),
    )
    def update_overview_from_filter(filter_data: dict | None):
        """
        Recompute and re-render all Overview components when global filters change.
        """
        user_type = "All"
        region = "All"
        gender = "All"
        day_type = "All"
        if filter_data and isinstance(filter_data, dict):
            user_type = filter_data.get("user_type", "All")
            region = filter_data.get("region", "All")
            gender = filter_data.get("gender", "All")
            day_type = filter_data.get("day_type", "All")

        # 1. Compute in-memory filtered slices (<2ms)
        kpis = get_filtered_overview_kpis(
            user_type=user_type,
            region=region,
            gender=gender,
            day_type=day_type,
        )
        daily_df = get_filtered_overview_daily(
            user_type=user_type,
            region=region,
            gender=gender,
            day_type=day_type,
        )

        # 2. Render updated components
        kpi_banner = render_kpi_banner(kpis)
        insights = render_key_insights(kpis)
        fig_trend = create_overview_daily_trend_chart(daily_df)

        return kpi_banner, insights, fig_trend
