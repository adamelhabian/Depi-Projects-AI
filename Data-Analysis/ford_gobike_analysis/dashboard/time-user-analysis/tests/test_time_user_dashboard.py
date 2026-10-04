"""
tests/test_time_user_dashboard.py – Verification Suite for Time & User Dashboard
=================================================================================
Validates data ingestion from Supabase, KPI computations, reactive filtering,
and generation of all 5 core visualizations.
"""

import sys
from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent.parent
if str(_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_MODULE_DIR))

import pandas as pd
from data_loader import load_clean_data
from utils.data_processing import filter_dataset, compute_kpi_summary
from charts.time_analysis import create_trips_by_hour_chart, create_trips_by_day_chart
from charts.user_analysis import (
    create_user_type_distribution_chart,
    create_user_type_hour_chart,
    create_age_group_distribution_chart,
)


def test_time_user_pipeline():
    print("\n" + "=" * 60)
    print("Running Member 4 Time & User Verification Suite...")
    print("=" * 60)

    # 1. Test Data Ingestion
    df = load_clean_data()
    assert not df.empty, "Dataset must not be empty"
    assert len(df) > 100000, f"Expected >100k trips from Supabase, got {len(df)}"
    print(f"[PASS] 1. Supabase ingestion verified: {len(df):,} trips loaded.")

    # 2. Test KPI Calculations
    kpis = compute_kpi_summary(df)
    assert kpis["total_trips"] == f"{len(df):,}"
    assert "%" in kpis["subscriber_pct"]
    assert ("AM" in kpis["peak_hour"] or "PM" in kpis["peak_hour"])
    assert "min" in kpis["avg_duration"]
    print(f"[PASS] 2. Headline KPIs verified: {kpis}")

    # 3. Test Filtering (Subscriber on Weekdays)
    df_sub_wd = filter_dataset(df, user_type="Subscriber", day_type="Weekday")
    assert not df_sub_wd.empty
    assert (df_sub_wd["user_type"] == "Subscriber").all()
    assert (df_sub_wd["weekend_flag"] == 0).all()
    print(f"[PASS] 3. Filtering verified: {len(df_sub_wd):,} weekday subscriber trips.")

    # 4. Test 5 Core Charts Generation
    f1 = create_trips_by_hour_chart(df)
    assert f1 is not None and len(f1.data) > 0
    print("[PASS] 4a. Hourly Demand chart generated.")

    f2 = create_trips_by_day_chart(df)
    assert f2 is not None and len(f2.data) > 0
    print("[PASS] 4b. Day-of-Week Volume chart generated.")

    f3 = create_user_type_distribution_chart(df)
    assert f3 is not None and len(f3.data) > 0
    print("[PASS] 4c. User Type distribution chart generated.")

    f4 = create_user_type_hour_chart(df)
    assert f4 is not None and len(f4.data) > 0
    print("[PASS] 4d. Hourly usage by user type chart generated.")

    f5 = create_age_group_distribution_chart(df)
    assert f5 is not None and len(f5.data) > 0
    print("[PASS] 4e. Age group distribution chart generated.")

    print("\n" + "=" * 60)
    print("ALL TIME & USER VERIFICATION CHECKS PASSED (100% SUCCESS)!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_time_user_pipeline()
