"""
callbacks/dashboard_callbacks.py – Reactive Controller for Time & User Dashboard
================================================================================
Coordinates filter updates, KPI computations, and reactive rendering of the
5 core Time & User visualizations from the Supabase dataset.
"""

from __future__ import annotations

import logging
from dash import Input, Output

from config import (
    # KPIs
    ID_KPI_TOTAL_TRIPS,
    ID_KPI_SUBSCRIBER_PCT,
    ID_KPI_PEAK_HOUR,
    ID_KPI_AVG_DURATION,
    # Filters
    ID_USER_FILTER,
    ID_DAY_FILTER,
    ID_GENDER_FILTER,
    ID_REGION_FILTER,
    # Charts
    ID_TRIPS_BY_HOUR,
    ID_TRIPS_BY_DAY,
    ID_USER_TYPE_DISTRIBUTION,
    ID_USER_TYPE_HOUR,
    ID_AGE_GROUP_DISTRIBUTION,
)
from data_loader import load_clean_data
from utils.data_processing import filter_dataset, compute_kpi_summary
from charts.time_analysis import (
    create_trips_by_hour_chart,
    create_trips_by_day_chart,
)
from charts.user_analysis import (
    create_user_type_distribution_chart,
    create_user_type_hour_chart,
    create_age_group_distribution_chart,
    create_trip_duration_distribution_chart,
)

logger = logging.getLogger(__name__)


def register_callbacks(app) -> None:
    """Register reactive callbacks for the Time & User dashboard."""

    @app.callback(
        [
            # 4 KPI Outputs
            Output(ID_KPI_TOTAL_TRIPS, "children"),
            Output(ID_KPI_SUBSCRIBER_PCT, "children"),
            Output(ID_KPI_PEAK_HOUR, "children"),
            Output(ID_KPI_AVG_DURATION, "children"),
            # 5 Chart Outputs
            Output(ID_TRIPS_BY_HOUR, "figure"),
            Output(ID_TRIPS_BY_DAY, "figure"),
            Output(ID_USER_TYPE_DISTRIBUTION, "figure"),
            Output(ID_USER_TYPE_HOUR, "figure"),
            Output(ID_AGE_GROUP_DISTRIBUTION, "figure"),
        ],
        [
            Input(ID_USER_FILTER, "value"),
            Input(ID_DAY_FILTER, "value"),
            Input(ID_GENDER_FILTER, "value"),
            Input(ID_REGION_FILTER, "value"),
        ],
    )
    def update_dashboard(
        selected_user: str | None,
        selected_day: str | None,
        selected_gender: str | None = "All",
        selected_region: str | None = "All",
    ):
        """Re-render KPIs and charts based on user membership, day classification, gender, and region."""
        df = load_clean_data()

        filtered_df = filter_dataset(
            df,
            user_type=selected_user,
            day_type=selected_day,
            gender=selected_gender,
            region=selected_region,
        )

        # 1. KPI Headline Metrics
        kpis = compute_kpi_summary(filtered_df)

        # 2. Five Core Time & User Visualizations
        fig_trips_by_hour = create_trips_by_hour_chart(filtered_df)
        fig_trips_by_day = create_trips_by_day_chart(filtered_df)
        fig_user_type_dist = create_user_type_distribution_chart(filtered_df)
        fig_duration_dist = create_trip_duration_distribution_chart(filtered_df)
        fig_age_dist = create_age_group_distribution_chart(filtered_df)

        peak_window_str = "08:00 & 17:00" if selected_user in (None, "All") else kpis["peak_hour"]

        return (
            kpis["total_trips"],
            kpis["subscriber_pct"],
            peak_window_str,
            kpis["avg_duration"],
            fig_trips_by_hour,
            fig_trips_by_day,
            fig_user_type_dist,
            fig_duration_dist,
            fig_age_dist,
        )