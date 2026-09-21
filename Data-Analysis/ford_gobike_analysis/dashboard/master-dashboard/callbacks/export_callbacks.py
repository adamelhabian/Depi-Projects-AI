"""
callbacks/export_callbacks.py – Global Analytical Summary Report Exporter
==========================================================================
Generates a comprehensive analytical summary CSV report whenever the user
clicks the 'Export Summary' button in the master navigation bar.
Captures active filter states, executive KPIs, key insights, daily trends,
top station flows, and hourly demand distributions into a downloadable file.
"""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime

import dash
from dash import Input, Output, State, dcc
import pandas as pd

from config import (
    ID_GLOBAL_DOWNLOAD_EXPORT,
    ID_GLOBAL_EXPORT_BTN,
    ID_GLOBAL_STORE,
    ID_URL,
)
from data_loader import (
    get_filtered_overview_daily,
    get_filtered_overview_hourly,
    get_filtered_overview_kpis,
    get_filtered_overview_stations,
)
from utils.metrics_calculator import (
    get_insight_commute_crest,
    get_insight_fleet_redistribution,
    get_insight_leisure_ratio,
    get_insight_subscription_dominance,
)

logger = logging.getLogger(__name__)


def generate_summary_csv(filter_data: dict | None, pathname: str | None = None) -> str:
    """
    Builds a comprehensive, well-structured CSV analytical report
    reflecting active filter slices and system insights.
    """
    filter_data = filter_data or {}
    user_type = filter_data.get("user_type", "All")
    region = filter_data.get("region", "All")
    gender = filter_data.get("gender", "All")
    day_type = filter_data.get("day_type", "All")
    timeframe = filter_data.get("timeframe", "all")

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
    stn_df = get_filtered_overview_stations(
        user_type=user_type,
        region=region,
        gender=gender,
        day_type=day_type,
    )
    hourly_df = get_filtered_overview_hourly(
        user_type=user_type,
        region=region,
        gender=gender,
        day_type=day_type,
    )

    buf = io.StringIO()
    writer = csv.writer(buf)

    # 1. Header & Metadata
    writer.writerow(["================================================================================"])
    writer.writerow(["FORD GOBIKE ANALYTICS PLATFORM - EXECUTIVE SUMMARY REPORT"])
    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    if pathname:
        writer.writerow([f"Active Module Route: {pathname}"])
    writer.writerow(["================================================================================"])
    writer.writerow([])

    # 2. Applied Global Filters
    writer.writerow(["[APPLIED GLOBAL FILTERS]"])
    writer.writerow(["Filter Dimension", "Selected Value"])
    writer.writerow(["Rider Membership", user_type])
    writer.writerow(["Metro Region", region])
    writer.writerow(["Gender Cohort", gender])
    writer.writerow(["Day Type", day_type])
    writer.writerow(["Timeframe Scope", timeframe.upper()])
    writer.writerow([])

    # 3. Executive KPIs
    writer.writerow(["[EXECUTIVE KPIS]"])
    writer.writerow(["Metric", "Value", "Description / Note"])
    writer.writerow(["Total Trips", kpis.get("total_trips", "N/A"), "Total trip volume matching active filters"])
    writer.writerow(["Unique Active Stations", kpis.get("unique_stations", "N/A"), "Unique stations with trip traffic"])
    writer.writerow(["Subscriber Share", kpis.get("subscriber_pct", "N/A"), "Percentage of commuter trips by subscribers"])
    writer.writerow(["Casual Share", kpis.get("casual_pct", "N/A"), "Percentage of leisure/single-ride customer trips"])
    writer.writerow(["Average Trip Duration", kpis.get("avg_duration", "N/A"), "Weighted mean trip duration in minutes"])
    writer.writerow(["Median Trip Duration", kpis.get("median_duration", "N/A"), "Median trip duration (reflects right skew)"])
    writer.writerow(["Peak Commute Rush Hour", kpis.get("peak_commute", "N/A"), "Hour recording highest system traffic"])
    writer.writerow(["Critical Rebalance Alerts", kpis.get("rebalance_alerts", "N/A"), "Stations with net imbalance >= 200 trips"])
    writer.writerow([])

    # 4. Computed Insights
    writer.writerow(["[OPERATIONAL & BEHAVIORAL INSIGHTS]"])
    writer.writerow(["Category", "Insight Summary"])
    writer.writerow(["Commute Crest", get_insight_commute_crest(kpis.get("busiest_day", "Thursday"))])
    writer.writerow(["Fleet Rebalancing", get_insight_fleet_redistribution(kpis.get("rebalance_alerts", "11"))])
    writer.writerow(["Subscription Dominance", get_insight_subscription_dominance(kpis.get("subscriber_pct", "90.5%"), kpis.get("avg_duration", "11.7 min"))])
    writer.writerow(["Leisure Exploration", get_insight_leisure_ratio()])
    writer.writerow([])

    # 5. Top 10 Busiest Stations
    if not stn_df.empty:
        writer.writerow(["[TOP 10 BUSIEST STATIONS]"])
        writer.writerow(["Rank", "Station Name", "Metro Region", "Total Trips"])
        for idx, row in enumerate(stn_df.head(10).itertuples(), start=1):
            writer.writerow([idx, row.station_name, row.region, row.trips])
        writer.writerow([])

    # 6. Daily Ridership Trajectory
    if not daily_df.empty:
        writer.writerow(["[DAILY RIDERSHIP TRAJECTORY]"])
        writer.writerow(["Date", "Formatted Date", "Trip Count", "Prior Week Baseline"])
        for row in daily_df.itertuples():
            prior = f"{int(row.prior_count)}" if hasattr(row, "prior_count") and not pd.isna(row.prior_count) else "N/A"
            writer.writerow([row.date_str, row.formatted_date, row.trip_count, prior])
        writer.writerow([])

    # 7. 24-Hour Commute Profile
    if not hourly_df.empty:
        writer.writerow(["[24-HOUR COMMUTE DEMAND PROFILE]"])
        writer.writerow(["Hour", "Trip Count", "Average Duration (min)"])
        for row in hourly_df.itertuples():
            writer.writerow([f"{row.hour:02d}:00", row.trip_count, row.avg_duration])

    return buf.getvalue()


def register_export_callbacks(app: dash.Dash) -> None:
    """Registers the Export Summary button callback."""

    @app.callback(
        Output(ID_GLOBAL_DOWNLOAD_EXPORT, "data"),
        Input(ID_GLOBAL_EXPORT_BTN, "n_clicks"),
        State(ID_GLOBAL_STORE, "data"),
        State(ID_URL, "pathname"),
        prevent_initial_call=True,
    )
    def export_summary_report(n_clicks: int | None, filter_data: dict | None, pathname: str | None):
        """Streams summary CSV file download on Export Summary button click."""
        if not n_clicks:
            return dash.no_update

        try:
            csv_content = generate_summary_csv(filter_data, pathname)

            # Build readable filename slug
            user_type = (filter_data or {}).get("user_type", "All").lower()
            region = (filter_data or {}).get("region", "All")
            region_slug = "all" if region == "All" else region.split()[0].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fordgobike_summary_{user_type}_{region_slug}_{timestamp}.csv"

            return dcc.send_string(csv_content, filename=filename, mime_type="text/csv")
        except Exception as exc:
            logger.exception("Export summary failed: %s", exc)
            return dash.no_update
