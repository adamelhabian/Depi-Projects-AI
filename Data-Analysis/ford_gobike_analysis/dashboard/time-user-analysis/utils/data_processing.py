"""
utils/data_processing.py – Analytical Engine for Time & User Analytics
======================================================================
Computes summary KPI metrics and analytical aggregations for temporal
and demographic user behavior without external UI dependencies.
"""

from __future__ import annotations

import pandas as pd


def filter_dataset(
    df: pd.DataFrame,
    user_type: str | None = None,
    day_type: str | None = None,
    gender: str | None = None,
    region: str | None = None,
) -> pd.DataFrame:
    """Filter dataset based on user type, day-of-week classification, gender, and geographic region."""
    filtered = df

    # 1. Filter by User Type
    if user_type and user_type not in {"All", "All Users"}:
        filtered = filtered[filtered["user_type"] == user_type]

    # 2. Filter by Day Type
    if day_type and day_type not in {"All", "All Days"}:
        if day_type in {"Weekday", "Weekdays", "Weekdays (Mon-Fri)"}:
            if "weekend_flag" in filtered.columns:
                filtered = filtered[filtered["weekend_flag"] == 0]
            elif "day_of_week" in filtered.columns:
                filtered = filtered[~filtered["day_of_week"].isin(["Saturday", "Sunday"])]
        elif day_type in {"Weekend", "Weekends", "Weekends (Sat-Sun)"}:
            if "weekend_flag" in filtered.columns:
                filtered = filtered[filtered["weekend_flag"] == 1]
            elif "day_of_week" in filtered.columns:
                filtered = filtered[filtered["day_of_week"].isin(["Saturday", "Sunday"])]

    # 3. Filter by Gender
    if gender and gender not in {"All", "All Genders"} and "member_gender" in filtered.columns:
        filtered = filtered[filtered["member_gender"] == gender]

    # 4. Filter by Region
    if region and region not in {"All", "All Regions"} and "region" in filtered.columns:
        filtered = filtered[filtered["region"] == region]

    return filtered


def compute_kpi_summary(df: pd.DataFrame) -> dict[str, str]:
    """
    Compute headline KPI summary metrics for the Time & User dashboard.
    Returns:
        - total_trips: formatted string (e.g. '174,724')
        - subscriber_pct: percentage string (e.g. '89.2%')
        - peak_hour: hour formatted string (e.g. '5:00 PM')
        - avg_duration: duration string (e.g. '11.7 min')
    """
    if df.empty:
        return {
            "total_trips": "0",
            "subscriber_pct": "0.0%",
            "peak_hour": "N/A",
            "avg_duration": "0.0 min",
        }

    total_trips = len(df)

    # Subscriber percentage
    if "user_type" in df.columns:
        sub_count = (df["user_type"] == "Subscriber").sum()
        sub_pct = (sub_count / total_trips) * 100.0
        sub_pct_str = f"{sub_pct:.1f}%"
    else:
        sub_pct_str = "N/A"

    # Peak hour
    if "hour" in df.columns and not df["hour"].isna().all():
        peak_h = int(df["hour"].mode().iloc[0])
        ampm = "AM" if peak_h < 12 else "PM"
        h12 = peak_h if 1 <= peak_h <= 12 else abs(peak_h - 12)
        if h12 == 0:
            h12 = 12
        peak_hour_str = f"{h12}:00 {ampm}"
    else:
        peak_hour_str = "N/A"

    # Average / Median duration
    if "duration_min" in df.columns and not df["duration_min"].isna().all():
        avg_dur = df["duration_min"].mean()
        avg_dur_str = f"{avg_dur:.1f} min"
    else:
        avg_dur_str = "N/A"

    return {
        "total_trips": f"{total_trips:,}",
        "subscriber_pct": sub_pct_str,
        "peak_hour": peak_hour_str,
        "avg_duration": avg_dur_str,
    }
