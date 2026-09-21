"""
utils package for Master Dashboard
"""
from utils.module_loader import get_station_module, get_time_user_module
from utils.metrics_calculator import (
    DEFAULT_KPIS,
    to_display_user_type,
    calc_total_trips,
    calc_mean_duration,
    calc_median_duration,
    calc_duration_by_user_type,
    calc_subscriber_pct,
    calc_unique_stations,
    calc_peak_hour,
    calc_busiest_day,
    calc_rebalance_alerts,
    compute_filtered_kpis,
    get_insight_commute_crest,
    get_insight_fleet_redistribution,
    get_insight_subscription_dominance,
    get_insight_leisure_ratio,
)

__all__ = [
    "get_station_module",
    "get_time_user_module",
    "DEFAULT_KPIS",
    "to_display_user_type",
    "calc_total_trips",
    "calc_mean_duration",
    "calc_median_duration",
    "calc_duration_by_user_type",
    "calc_subscriber_pct",
    "calc_unique_stations",
    "calc_peak_hour",
    "calc_busiest_day",
    "calc_rebalance_alerts",
    "compute_filtered_kpis",
    "get_insight_commute_crest",
    "get_insight_fleet_redistribution",
    "get_insight_subscription_dominance",
    "get_insight_leisure_ratio",
]
