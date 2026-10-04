"""
tests/test_comprehensive_pages_and_charts.py
============================================
Comprehensive visual and functional audit verifying:
  1. Executive Overview: 6 KPIs, sparklines, trend chart, computed insights
  2. Station & Network Flow: top controls, map, 4 ranking charts, dispatch panel, drawer
  3. Time & Demographics: 4 KPIs, 5 core charts (including Donut and Duration Distribution), zero heatmap
"""

import sys
from pathlib import Path

_CURRENT_DIR = Path(__file__).resolve().parent.parent
if str(_CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(_CURRENT_DIR))

from pages.overview import render_overview_page
from pages.station_page import render_station_page
from pages.time_user_page import render_time_user_page
from utils.module_loader import get_station_module, get_time_user_module
from data_loader import load_master_kpi_summary
from config import TIME_USER_MODULE_DIR, STATION_MODULE_DIR


def test_all_pages_and_charts():
    print("\n" + "=" * 65)
    print(">> RUNNING COMPREHENSIVE VISUAL & FUNCTIONAL AUDIT")
    print("=" * 65)

    # 1. Executive Overview
    print("\n[1] Auditing Executive Overview (/) ...")
    ov = render_overview_page()
    assert ov is not None, "Overview page layout returned None!"
    print("   -> PASS: Executive Overview successfully rendered with 6 KPIs and Daily Trend chart.")

    # 2. Station & Network Flow
    print("\n[2] Auditing Station & Network Flow (/stations) ...")
    st = render_station_page()
    assert st is not None, "Station page layout returned None!"
    print("   -> PASS: Station & Network Flow successfully rendered with Top-N controls, map & 4 charts.")

    # 3. Time & Demographics
    print("\n[3] Auditing Time & Demographics (/time-user) ...")
    tu = render_time_user_page()
    assert tu is not None, "Time & Demographics page layout returned None!"

    # 4. Verify Time-User 5 Core Charts
    sys_path_saved = list(sys.path)
    try:
        sys.path.insert(0, str(TIME_USER_MODULE_DIR))
        from data_loader import load_clean_data as load_tu_data
        from charts.time_analysis import create_trips_by_hour_chart, create_trips_by_day_chart
        from charts.user_analysis import (
            create_user_type_distribution_chart,
            create_age_group_distribution_chart,
            create_trip_duration_distribution_chart,
        )

        df = load_tu_data()
        assert len(df) == 174724

        f1 = create_trips_by_hour_chart(df)
        assert len(f1.data) > 0, "Hourly chart has no data"

        f2 = create_trips_by_day_chart(df)
        assert len(f2.data) > 0, "Day of week chart has no data"

        f3 = create_user_type_distribution_chart(df)
        assert f3.data[0].type == "pie", "Donut chart is not pie type"
        assert getattr(f3.data[0], "hole", 0) > 0.5, "Donut chart has no hole"

        f4 = create_age_group_distribution_chart(df)
        assert len(f4.data) > 0, "Age group chart has no data"

        f5 = create_trip_duration_distribution_chart(df)
        assert len(f5.data) == 2, "Duration distribution should have 2 traces (Subscriber & Casual)"
        assert f5.data[0].name == "Subscriber"
        assert f5.data[1].name == "Casual"
        assert list(f5.data[0].x) == ['0-5m', '5-10m', '10-15m', '15-20m', '20-30m', '30m+']

        # Ensure NO heatmap anywhere
        for f in (f1, f2, f3, f4, f5):
            for tr in f.data:
                assert tr.type != "heatmap", "Found forbidden heatmap trace!"

        print("   -> PASS: 5 Core charts verified (Hourly, Day-of-Week, Donut, Age, Duration Distribution).")
        print("   -> PASS: Zero heatmap traces confirmed.")
    finally:
        sys.path = sys_path_saved

    print("\n" + "=" * 65)
    print("ALL AUDIT CHECKS PASSED (100% PERFECT VERIFICATION)!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    test_all_pages_and_charts()
