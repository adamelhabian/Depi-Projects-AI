import sys
from pathlib import Path
import dash

# Set up paths
_REPO_ROOT = Path(r"d:/Depi R5/DA Final Project/Phase 1/EDA/Depi-Projects-AI")
_STATION_DIR = _REPO_ROOT / "Data-Analysis/ford_gobike_analysis/dashboard/station-trip-analysis"
sys.path.insert(0, str(_STATION_DIR))

from callbacks.dashboard_callbacks import _extract_station_name, register_callbacks
from config import ID_MAP, ID_TOP_STATIONS, ID_DRAWER_CLOSE_BTN, ID_SELECTED_STATION_STORE, ID_INSPECTOR_CONTAINER

def test_drawer_and_click():
    print("Testing _extract_station_name with 1D customdata...")
    click_1d = {"points": [{"customdata": ["Market St at 10th St"], "pointIndex": 4}]}
    stn = _extract_station_name(click_1d)
    assert stn == "Market St at 10th St", f"Expected 'Market St at 10th St', got {stn}"

    print("Testing _extract_station_name with scalar customdata...")
    click_scalar = {"points": [{"customdata": "Powell St BART Station (Market St at 4th St)", "pointIndex": 1}]}
    stn = _extract_station_name(click_scalar)
    assert stn == "Powell St BART Station (Market St at 4th St)", f"Expected Powell St, got {stn}"

    print("Testing _extract_station_name with bar chart y value...")
    click_y = {"points": [{"y": "San Francisco Caltrain (Townsend St at 4th St)"}]}
    stn = _extract_station_name(click_y)
    assert stn == "San Francisco Caltrain (Townsend St at 4th St)", f"Expected Caltrain, got {stn}"

    print("Testing _extract_station_name with hover text regex...")
    click_text = {"points": [{"text": "<b>San Francisco Ferry Building</b><br>Trips: 15,000"}]}
    stn = _extract_station_name(click_text)
    assert stn == "San Francisco Ferry Building", f"Expected Ferry Building, got {stn}"

    print("Testing callback logic on close button mounting vs clicking...")
    # Test close button mounting with n_clicks=0 -> Must NOT close
    app = dash.Dash(__name__)
    register_callbacks(app)
    
    # Check handle_station_click directly from callback map
    cb_fn = None
    for k, v in app.callback_map.items():
        if ID_SELECTED_STATION_STORE in k:
            cb_fn = v["callback"].__wrapped__ if hasattr(v["callback"], "__wrapped__") else v["callback"]
            break
    
    assert cb_fn is not None, "handle_station_click callback not found!"

    # Simulate Dash ctx
    from unittest.mock import patch, MagicMock
    with patch("callbacks.dashboard_callbacks.ctx") as mock_ctx:
        # 1. Close button mounted with 0 clicks -> should be no_update
        mock_ctx.triggered_id = ID_DRAWER_CLOSE_BTN
        res = cb_fn(None, None, 0)
        assert res == dash.no_update, f"Expected dash.no_update on mount, got {res}"

        # 2. Close button clicked with 1 click -> should return None (closed)
        mock_ctx.triggered_id = ID_DRAWER_CLOSE_BTN
        res = cb_fn(None, None, 1)
        assert res is None, f"Expected None on close button click, got {res}"

        # 3. Map marker clicked -> should return station
        mock_ctx.triggered_id = ID_MAP
        res = cb_fn(click_1d, None, 0)
        assert res == "Market St at 10th St", f"Expected station name on map click, got {res}"

        # 4. Map empty area clicked -> should return None (closed)
        mock_ctx.triggered_id = ID_MAP
        res = cb_fn(None, None, 0)
        assert res is None, f"Expected None on empty map click, got {res}"
        res_empty_points = cb_fn({"points": []}, None, 0)
        assert res_empty_points is None, f"Expected None on empty points map click, got {res_empty_points}"

    print("ALL MAP CLICK & DRAWER TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_drawer_and_click()
