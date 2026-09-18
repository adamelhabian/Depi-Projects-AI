"""
callbacks/dashboard_callbacks.py – Reactive Event & Analytics Controller
========================================================================
Coordinates filter updates, regional zooming, on-map corridor rendering,
interactive station click inspections, and CSV exports.

Design Principles:
  - Thin callback pattern: business calculations & Plotly themes reside in utils/ and charts/.
  - Station clicks on either the Map or the Top Stations chart seamlessly update the Station Inspector.
  - Graceful edge-case handling for empty filters or unlocated stations.
"""

from __future__ import annotations

import copy
import logging
import pandas as pd
import dash
from dash import Input, Output, State, ctx, dcc

from config import (
    ID_MAP,
    ID_TOP_STATIONS,
    ID_TOP_ROUTES,
    ID_FLOW_IMBALANCE,
    ID_ROUND_TRIP_CHART,
    ID_INSPECTOR_CONTAINER,
    ID_DISPATCH_CONTAINER,
    ID_SELECTED_STATION_STORE,
    ID_USER_FILTER,
    ID_TOP_N_SLIDER,
    ID_REGION_FILTER,
    ID_MAP_FLOW_LINES_TOGGLE,
    ID_DOWNLOAD_BTN,
    ID_DOWNLOAD_DATA,
    ID_DRAWER_CLOSE_BTN,
    ID_DRAWER_FOCUS_BTN,
)
from data_loader import load_clean_data
from utils.data_processing import (
    compute_canonical_station_metrics,
    compute_top_stations,
    compute_top_routes,
    compute_flow_imbalance,
    compute_round_trip_hotspots,
    compute_station_deep_dive,
    compute_smart_dispatch_pairs,
)
from charts.geo_map import create_station_map
from charts.station_analysis import (
    create_top_stations_chart,
    create_flow_imbalance_chart,
    create_round_trip_hotspots_chart,
)
from charts.trip_analysis import create_top_routes_chart
from components.station_inspector import render_station_inspector
from components.dispatch_panel import render_dispatch_panel

logger = logging.getLogger(__name__)


def _extract_station_name(click_data: dict | None) -> str | None:
    """Safely parse clicked station name from map scatter or horizontal bar chart."""
    if not click_data or "points" not in click_data or not click_data["points"]:
        return None
    pt = click_data["points"][0]

    # 1. Inspect customdata (preferred for map and bars)
    cd = pt.get("customdata")
    if isinstance(cd, (list, tuple)) and len(cd) > 0:
        return str(cd[0])
    if isinstance(cd, str):
        return cd

    # 2. Inspect category y-axis value
    y_val = pt.get("y")
    if isinstance(y_val, str):
        return y_val

    return None


def register_callbacks(app: dash.Dash) -> None:
    """
    Register all Member 5 dashboard callbacks onto the Dash application instance.
    """

    # -----------------------------------------------------------------------
    # 1. Main Dashboard Update (Filters -> Figures & Dispatch Panel)
    # -----------------------------------------------------------------------
    @app.callback(
        [
            Output(ID_MAP, "figure"),
            Output(ID_TOP_STATIONS, "figure"),
            Output(ID_TOP_ROUTES, "figure"),
            Output(ID_FLOW_IMBALANCE, "figure"),
            Output(ID_ROUND_TRIP_CHART, "figure"),
            Output(ID_DISPATCH_CONTAINER, "children"),
        ],
        [
            Input(ID_USER_FILTER, "value"),
            Input(ID_TOP_N_SLIDER, "value"),
            Input(ID_REGION_FILTER, "value"),
            Input(ID_MAP_FLOW_LINES_TOGGLE, "value"),
        ],
    )
    def update_dashboard(
        selected_user: str | None,
        top_n: int | None,
        selected_region: str | None,
        flow_lines_toggle: list[str] | None,
    ):
        """
        Respond to User Type, Top N, Region, and Map Overlay filter changes.
        """
        n = int(top_n) if top_n else 10
        user_filter = selected_user or "All"
        region_filter = selected_region or "All"
        show_flow_lines = "show" in (flow_lines_toggle or [])

        # 1. Load cached cleaned dataset
        df = load_clean_data()

        # 2. User Membership filtering
        if user_filter != "All" and "user_type" in df.columns:
            filtered_df = df[df["user_type"] == user_filter]
        else:
            filtered_df = df

        # 3. Canonical station metrics for the active user slice
        station_metrics = compute_canonical_station_metrics(filtered_df)

        # 4. Regional filtering
        if region_filter != "All":
            region_stns = set(
                station_metrics[station_metrics["region"] == region_filter]["station_name"]
            )
            station_metrics_view = station_metrics[station_metrics["region"] == region_filter]
            df_view = filtered_df[filtered_df["start_station_name"].isin(region_stns)]
        else:
            station_metrics_view = station_metrics
            df_view = filtered_df

        # 5. Analytical subsets
        top_stations = compute_top_stations(station_metrics_view, top_n=n)
        top_routes = compute_top_routes(df_view, top_n=n)
        flow_imbalance = compute_flow_imbalance(station_metrics_view, top_n=n)
        round_trips = compute_round_trip_hotspots(df_view, top_n=n)
        dispatch_pairs = compute_smart_dispatch_pairs(station_metrics_view, max_pairs=3)

        # 5b. Compute top destination map (station → its #1 destination)
        top_dest_map = {}
        if not filtered_df.empty and "start_station_name" in filtered_df.columns:
            valid_trips = filtered_df[
                (filtered_df["start_station_name"].notna())
                & (filtered_df["end_station_name"].notna())
                & (filtered_df["start_station_name"] != filtered_df["end_station_name"])
            ]
            if not valid_trips.empty:
                dest_counts = (
                    valid_trips
                    .groupby(["start_station_name", "end_station_name"], observed=True)
                    .size()
                    .reset_index(name="cnt")
                )
                idx_max = dest_counts.groupby("start_station_name", observed=True)["cnt"].idxmax()
                top_pairs = dest_counts.loc[idx_max]
                top_dest_map = dict(
                    zip(top_pairs["start_station_name"], top_pairs["end_station_name"])
                )

        # 5c. Total network traffic for percentage calculations
        total_network_traffic = int(station_metrics_view["total_traffic"].sum()) if not station_metrics_view.empty else 0

        # 6. Generate Figures
        fig_map = create_station_map(
            station_metrics,
            region=region_filter,
            top_routes=top_routes,
            show_flow_lines=show_flow_lines,
            top_dest_map=top_dest_map,
        )
        fig_stations = create_top_stations_chart(top_stations, total_network_traffic=total_network_traffic)
        fig_routes = create_top_routes_chart(top_routes)
        fig_imbalance = create_flow_imbalance_chart(flow_imbalance)
        fig_round_trip = create_round_trip_hotspots_chart(round_trips)

        # 7. Render Dispatch Component
        dispatch_children = render_dispatch_panel(dispatch_pairs)

        return (
            fig_map,
            fig_stations,
            fig_routes,
            fig_imbalance,
            fig_round_trip,
            dispatch_children,
        )

    # -----------------------------------------------------------------------
    # 2. Station Selection Store (Captures clicks from Map, Bar Chart, & Close Button)
    # -----------------------------------------------------------------------
    @app.callback(
        Output(ID_SELECTED_STATION_STORE, "data"),
        [
            Input(ID_MAP, "clickData"),
            Input(ID_TOP_STATIONS, "clickData"),
            Input(ID_DRAWER_CLOSE_BTN, "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def handle_station_click(map_click, bar_click, close_clicks):
        """Extract station name from the most recent user interaction, or reset on close."""
        triggered = ctx.triggered_id
        if triggered == ID_DRAWER_CLOSE_BTN:
            return None
        elif triggered == ID_MAP and map_click:
            return _extract_station_name(map_click)
        elif triggered == ID_TOP_STATIONS and bar_click:
            return _extract_station_name(bar_click)
        return dash.no_update

    # -----------------------------------------------------------------------
    # 3. Interactive Station Profile Inspector (Side Drawer)
    # -----------------------------------------------------------------------
    @app.callback(
        [
            Output(ID_INSPECTOR_CONTAINER, "children"),
            Output(ID_INSPECTOR_CONTAINER, "className"),
        ],
        [
            Input(ID_SELECTED_STATION_STORE, "data"),
            Input(ID_USER_FILTER, "value"),
            Input(ID_REGION_FILTER, "value"),
            Input(ID_TOP_N_SLIDER, "value"),
        ],
    )
    def update_station_inspector(
        selected_station: str | None,
        selected_user: str | None,
        selected_region: str | None,
        top_n: int | None,
    ):
        """Update drill-down drawer whenever station or filter parameters change."""
        if not selected_station:
            return render_station_inspector(None), "station-drawer drawer-closed"

        df = load_clean_data()
        user_filter = selected_user or "All"
        if user_filter != "All" and "user_type" in df.columns:
            df_filtered = df[df["user_type"] == user_filter]
        else:
            df_filtered = df

        station_metrics = compute_canonical_station_metrics(df_filtered)

        region_filter = selected_region or "All"
        if region_filter != "All":
            region_stns = set(
                station_metrics[station_metrics["region"] == region_filter]["station_name"]
            )
            station_metrics_view = station_metrics[station_metrics["region"] == region_filter]
            df_view = df_filtered[df_filtered["start_station_name"].isin(region_stns)]
        else:
            station_metrics_view = station_metrics
            df_view = df_filtered

        # If station is not present in the current regional view, dismiss drawer
        if selected_station not in station_metrics_view["station_name"].values:
            return render_station_inspector(None), "station-drawer drawer-closed"

        profile = compute_station_deep_dive(df_view, selected_station, station_metrics_view)
        return render_station_inspector(profile), "station-drawer drawer-open"

    # -----------------------------------------------------------------------
    # 3b. Focus Map on Selected Station
    # -----------------------------------------------------------------------
    @app.callback(
        Output(ID_MAP, "figure", allow_duplicate=True),
        Input(ID_DRAWER_FOCUS_BTN, "n_clicks"),
        [
            State(ID_SELECTED_STATION_STORE, "data"),
            State(ID_MAP, "figure"),
        ],
        prevent_initial_call=True,
    )
    def focus_map_on_station(n_clicks: int | None, selected_station: str | None, current_fig: dict | None):
        """Re-center and zoom map viewport directly onto the inspected station."""
        if not n_clicks or not selected_station or not current_fig:
            return dash.no_update

        df = load_clean_data()
        stn_match = df[df["start_station_name"] == selected_station]
        if stn_match.empty:
            stn_match = df[df["end_station_name"] == selected_station]

        if stn_match.empty:
            return dash.no_update

        lat = float(stn_match.iloc[0]["start_station_latitude"]) if "start_station_latitude" in stn_match.columns else None
        lon = float(stn_match.iloc[0]["start_station_longitude"]) if "start_station_longitude" in stn_match.columns else None

        if lat is None or lon is None or pd.isna(lat) or pd.isna(lon):
            return dash.no_update

        fig_dict = copy.deepcopy(current_fig)
        map_key = "map" if "map" in fig_dict.get("layout", {}) else "mapbox"

        if "layout" in fig_dict and map_key in fig_dict["layout"]:
            fig_dict["layout"][map_key]["center"] = {"lat": lat, "lon": lon}
            fig_dict["layout"][map_key]["zoom"] = 15.0

        return fig_dict

    # -----------------------------------------------------------------------
    # 4. CSV Dataset Export
    # -----------------------------------------------------------------------
    @app.callback(
        Output(ID_DOWNLOAD_DATA, "data"),
        Input(ID_DOWNLOAD_BTN, "n_clicks"),
        [
            State(ID_USER_FILTER, "value"),
            State(ID_REGION_FILTER, "value"),
        ],
        prevent_initial_call=True,
    )
    def export_station_csv(n_clicks: int, selected_user: str | None, selected_region: str | None):
        """Generate and stream CSV download of station metrics matching active filters."""
        if not n_clicks:
            return dash.no_update

        df = load_clean_data()
        user_filter = selected_user or "All"
        if user_filter != "All" and "user_type" in df.columns:
            df = df[df["user_type"] == user_filter]

        metrics = compute_canonical_station_metrics(df)
        reg = selected_region or "All"
        if reg != "All":
            metrics = metrics[metrics["region"] == reg]

        # Clean filename slug
        slug = reg.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        filename = f"fordgobike_station_metrics_{slug}.csv"
        return dcc.send_data_frame(metrics.to_csv, filename, index=False)

    # -----------------------------------------------------------------------
    # 5. Live Top-N Scope Badge Update
    # -----------------------------------------------------------------------
    @app.callback(
        Output("m5-slider-scope-badge", "children"),
        Input(ID_TOP_N_SLIDER, "value"),
    )
    def update_scope_badge(val):
        """Update top ranking badge smoothly to show exact selected value (e.g. Top 7, Top 13)."""
        v = int(val) if val else DEFAULT_TOP_N
        return f"Top {v}"
