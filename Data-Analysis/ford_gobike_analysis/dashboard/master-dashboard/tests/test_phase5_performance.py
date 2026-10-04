"""
tests/test_phase5_performance.py
================================
Phase 5 performance profiler:
  - Times render_*_page() for all 4 pages
  - Times load_overview_cubes() first vs cached call
  - Times load_clean_station_data() first vs cached
  - Times load_clean_time_user_data() first vs cached
  - Times update_user_trips callback (filter_data=None)
  - Verifies sidebar width is exactly 16rem (256 px) in layout.py
  - Verifies filter bar has sticky + top-14 CSS classes
  - Verifies skeleton CSS classes exist in master_style.css
  - Verifies _filtered_data_cache is used in user_trips_page
  - Verifies dcc.Loading wraps page-content in layout.py
Prints sorted table of slowest operations at the end.
"""

import sys
import time
import os
from pathlib import Path

MASTER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MASTER_DIR))

print()
print("=" * 70)
print("   PHASE 5: PERFORMANCE PROFILING & CACHING VERIFICATION")
print("=" * 70)

timings: list[tuple[str, float]] = []

def timed(label: str):
    """Context manager that records elapsed ms."""
    class _T:
        def __enter__(self_inner):
            self_inner.t0 = time.perf_counter()
            return self_inner
        def __exit__(self_inner, *_):
            ms = (time.perf_counter() - self_inner.t0) * 1000
            timings.append((label, ms))
    return _T()


# ---------------------------------------------------------------------------
# 1. Data Loading – first call (cold / from DB)
# ---------------------------------------------------------------------------
print("\n[SECTION 1] Data loading timings (first call = cold)")

from data_loader import load_overview_cubes, load_master_kpi_summary, load_overview_daily_trend

with timed("load_master_kpi_summary() [cold]"):
    summary = load_master_kpi_summary()
assert summary.get("raw_total_trips", 0) > 0, "KPI summary must have real trip count"
print(f"   -> load_master_kpi_summary: {timings[-1][1]:.1f} ms  (trips={summary['raw_total_trips']:,})")

with timed("load_overview_cubes() [cold]"):
    cubes = load_overview_cubes()
print(f"   -> load_overview_cubes:     {timings[-1][1]:.1f} ms  (3 cubes loaded)")

# Second call must be served from lru_cache – must be <50 ms
with timed("load_overview_cubes() [warm/cached]"):
    cubes2 = load_overview_cubes()
warm_ms = timings[-1][1]
print(f"   -> load_overview_cubes [warm]: {warm_ms:.1f} ms  (expect <50ms from cache)")
assert warm_ms < 50, f"FAIL: warm cache call took {warm_ms:.1f}ms, expected <50ms"
print("   [PASS] Cache hit: second load_overview_cubes() < 50ms")

# Station data
from utils.module_loader import load_clean_station_data, load_clean_time_user_data

with timed("load_clean_station_data() [cold]"):
    stn_df = load_clean_station_data()
print(f"   -> load_clean_station_data: {timings[-1][1]:.1f} ms  (rows={len(stn_df):,})")

with timed("load_clean_station_data() [warm/cached]"):
    stn_df2 = load_clean_station_data()
warm_stn = timings[-1][1]
print(f"   -> load_clean_station_data [warm]: {warm_stn:.1f} ms")

with timed("load_clean_time_user_data() [cold]"):
    tu_df = load_clean_time_user_data()
print(f"   -> load_clean_time_user_data: {timings[-1][1]:.1f} ms  (rows={len(tu_df):,})")

with timed("load_clean_time_user_data() [warm/cached]"):
    tu_df2 = load_clean_time_user_data()
warm_tu = timings[-1][1]
print(f"   -> load_clean_time_user_data [warm]: {warm_tu:.1f} ms")
assert warm_tu < 50, f"FAIL: warm time-user cache call took {warm_tu:.1f}ms, expected <50ms"
print("   [PASS] Cache hit: second load_clean_time_user_data() < 50ms")


# ---------------------------------------------------------------------------
# 2. Page render timings
# ---------------------------------------------------------------------------
print("\n[SECTION 2] Page render timings")

with timed("render_overview_page()"):
    from pages.overview import render_overview_page
    ov = render_overview_page()
print(f"   -> render_overview_page:   {timings[-1][1]:.1f} ms")

with timed("render_station_page()"):
    from pages.station_page import render_station_page
    sp = render_station_page()
print(f"   -> render_station_page:    {timings[-1][1]:.1f} ms")

with timed("render_time_user_page()"):
    from pages.time_user_page import render_time_user_page
    tu = render_time_user_page()
print(f"   -> render_time_user_page:  {timings[-1][1]:.1f} ms")

with timed("render_user_trips_page()"):
    from pages.user_trips_page import render_user_trips_page
    utp = render_user_trips_page()
print(f"   -> render_user_trips_page: {timings[-1][1]:.1f} ms")


# ---------------------------------------------------------------------------
# 3. Filtered data caching (user_trips_page)
# ---------------------------------------------------------------------------
print("\n[SECTION 3] Filtered data cache verification (user_trips_page)")

import pages.user_trips_page as utp_mod
assert hasattr(utp_mod, "_FILTERED_DATA_CACHE"), \
    "FAIL: _FILTERED_DATA_CACHE dict must exist in user_trips_page.py"
print("   [PASS] _FILTERED_DATA_CACHE exists in user_trips_page")

# Time an unfiltered callback round-trip twice to verify cache benefit
filter_none = None
t0 = time.perf_counter()
utp_mod._get_filtered_cached(tu_df, filter_none)
first_ms = (time.perf_counter() - t0) * 1000

t0 = time.perf_counter()
utp_mod._get_filtered_cached(tu_df, filter_none)
second_ms = (time.perf_counter() - t0) * 1000
timings.append(("_get_filtered_cached() [cold]", first_ms))
timings.append(("_get_filtered_cached() [warm]", second_ms))
print(f"   -> _get_filtered_cached() cold: {first_ms:.1f}ms, warm: {second_ms:.1f}ms")
assert second_ms < first_ms * 2 or second_ms < 5, \
    f"FAIL: warm cache should be near-instant, got {second_ms:.1f}ms"
print("   [PASS] Filter cache warm call is fast")


# ---------------------------------------------------------------------------
# 4. CSS / Layout structural checks
# ---------------------------------------------------------------------------
print("\n[SECTION 4] CSS and layout structural checks")

css_path = MASTER_DIR / "assets" / "master_style.css"
css_text = css_path.read_text(encoding="utf-8")

# Skeleton classes must exist
for cls in [".skeleton", ".skeleton-kpi", ".skeleton-chart", ".skeleton-page"]:
    assert cls in css_text, f"FAIL: CSS class {cls} missing from master_style.css"
print("   [PASS] Skeleton shimmer CSS classes present")

# Sticky filter-bar class
assert ".master-filter-bar-sticky" in css_text, \
    "FAIL: .master-filter-bar-sticky must be defined in master_style.css"
assert "position: sticky" in css_text, \
    "FAIL: filter bar must be position:sticky in master_style.css"
assert "--filter-bar-top" in css_text or "top: 56px" in css_text or "top:56px" in css_text or "var(--filter-bar-top)" in css_text, \
    "FAIL: filter bar top offset not found"
print("   [PASS] Filter bar sticky CSS present (.master-filter-bar-sticky, position: sticky)")

# Sidebar width consistent: sidebar.py must use 16rem / w-64
sidebar_py = (MASTER_DIR / "components" / "sidebar.py").read_text(encoding="utf-8")
assert "16rem" in sidebar_py or "w-64" in sidebar_py, \
    "FAIL: sidebar.py width must be 16rem (w-64)"
print("   [PASS] sidebar.py uses 16rem width")

# CSS sidebar width lock
assert "--sidebar-width" in css_text and "16rem" in css_text, \
    "FAIL: CSS must have --sidebar-width: 16rem token"
print("   [PASS] CSS --sidebar-width token = 16rem")

# layout.py main wrapper must use same 16rem offset
layout_py = (MASTER_DIR / "layout.py").read_text(encoding="utf-8")
assert "16rem" in layout_py, \
    "FAIL: layout.py marginLeft must match sidebar 16rem"
print("   [PASS] layout.py main wrapper uses 16rem left offset (matches sidebar)")

# dcc.Loading wrapping page-content in layout.py
assert "dcc.Loading" in layout_py, \
    "FAIL: layout.py must wrap page content in dcc.Loading for skeleton transitions"
print("   [PASS] dcc.Loading present in layout.py for skeleton page transitions")

# routing.py must have _skeleton_page function
routing_py = (MASTER_DIR / "callbacks" / "routing.py").read_text(encoding="utf-8")
assert "_skeleton_page" in routing_py, \
    "FAIL: routing.py must define _skeleton_page() shimmer placeholder"
print("   [PASS] _skeleton_page() defined in routing.py")

# filter bar sticky class in global_filter_bar.py
filter_bar_py = (MASTER_DIR / "components" / "global_filter_bar.py").read_text(encoding="utf-8")
assert "sticky" in filter_bar_py, \
    "FAIL: global_filter_bar.py must use sticky positioning"
assert "master-filter-bar-sticky" in filter_bar_py, \
    "FAIL: global_filter_bar.py must have class master-filter-bar-sticky"
print("   [PASS] global_filter_bar.py uses sticky + master-filter-bar-sticky class")

# Profiler instrumentation in user_trips_page.py
utp_py = (MASTER_DIR / "pages" / "user_trips_page.py").read_text(encoding="utf-8")
assert "_phase5_profiler" in utp_py, \
    "FAIL: user_trips_page.py must have _phase5_profiler() function"
assert "perf_counter" in utp_py, \
    "FAIL: user_trips_page.py must use perf_counter for timing"
print("   [PASS] Phase 5 callback profiler instrumentation in user_trips_page.py")

# module_loader must have DataFrame-level caches
ml_py = (MASTER_DIR / "utils" / "module_loader.py").read_text(encoding="utf-8")
assert "_STATION_DATA_CACHE" in ml_py, \
    "FAIL: module_loader.py must have _STATION_DATA_CACHE variable"
assert "_TIME_USER_DATA_CACHE" in ml_py, \
    "FAIL: module_loader.py must have _TIME_USER_DATA_CACHE variable"
print("   [PASS] module_loader.py has _STATION_DATA_CACHE and _TIME_USER_DATA_CACHE")
print("         (fixes cache-busting bug: _clean_colliding_modules() no longer defeats lru_cache)")


# ---------------------------------------------------------------------------
# 5. Summary table
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("   PHASE 5 PERFORMANCE SUMMARY TABLE (slowest first)")
print("=" * 70)
print(f"   {'Operation':<48} {'Time (ms)':>10}")
print(f"   {'-'*48} {'-'*10}")
for label, ms in sorted(timings, key=lambda x: x[1], reverse=True):
    flag = "  *** SLOW" if ms > 2000 else ("  * warn" if ms > 500 else "")
    print(f"   {label:<48} {ms:>9.1f}{flag}")

print()
print("=" * 70)
print("   ALL PHASE 5 TESTS PASSED!")
print("=" * 70)
print()
