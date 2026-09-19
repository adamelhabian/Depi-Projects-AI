"""
callbacks/dashboard_callbacks.py – Reactive Event & Analytics Controller
========================================================================
Coordinates filter updates, regional zooming, on-map corridor rendering,
interactive station click inspections, and CSV exports.

This module ALSO registers clientside-only callbacks (no server roundtrip)
that power the sidebar navigation:

  C1. Section switching       – nav button click -> active section store
  C2. Section visibility      – active section store -> show/hide 4 wrappers
  C3. Active nav styling      – active section store -> active/inactive classes
  C4. Anchor scroll           – sub-link click -> smooth scroll to target group
  C5. Mobile drawer toggle    – hamburger/backdrop click -> open/close store
  C6. Mobile drawer view      – store -> show/hide drawer + backdrop
  C7. Filter panel visibility – active section -> show/hide the global
                                filter panel (visible ONLY on Station Analysis)

All navigation uses `dash_clientside.callback_context.triggered_id` to
identify the clicked element — the officially supported mechanism inside
Dash clientside callbacks.

The main `update_dashboard` server callback is untouched, and the filter
panel itself (components/filter_panel.py) is unchanged: only its wrapper
visibility is toggled.
"""

from __future__ import annotations

import copy
import logging
import pandas as pd
import dash
from dash import Input, Output, State, ctx, dcc, clientside_callback

from config import (
    # Charts
    ID_MAP,
    ID_TOP_STATIONS,
    ID_TOP_ROUTES,
    ID_FLOW_IMBALANCE,
    ID_ROUND_TRIP_CHART,
    ID_TRIPS_BY_HOUR,
    ID_DAY_HOUR_HEATMAP,
    ID_AVG_DURATION_BY_HOUR,
    ID_WEEKDAY_WEEKEND_DURATION,
    ID_USER_TYPE_DISTRIBUTION,
    ID_USER_TYPE_HOUR,
    ID_AVG_DURATION_BY_USER_TYPE,
    ID_AGE_GROUP_DISTRIBUTION,
    ID_GENDER_DISTRIBUTION,
    ID_USER_TYPE_BY_AGE_GROUP,

    # Containers & stores
    ID_INSPECTOR_CONTAINER,
    ID_DISPATCH_CONTAINER,
    ID_SELECTED_STATION_STORE,

    # Filters
    ID_USER_FILTER,
    ID_TOP_N_SLIDER,
    ID_REGION_FILTER,
    ID_MAP_FLOW_LINES_TOGGLE,
    ID_DOWNLOAD_BTN,
    ID_DOWNLOAD_DATA,
    ID_DRAWER_CLOSE_BTN,
    ID_DRAWER_FOCUS_BTN,

    # Sidebar
    ID_ACTIVE_SECTION_STORE,
    ID_ACTIVE_ANCHOR_STORE,
    ID_MOBILE_MENU_STORE,
    ID_MOBILE_MENU_TOGGLE,
    ID_MOBILE_BACKDROP,
    ID_MOBILE_SIDEBAR,
    ID_SECTION_STATION,
    ID_SECTION_TIME,
    ID_SECTION_USER,
    ID_SECTION_DISPATCH,
    ID_FILTER_PANEL_WRAPPER,

    # Desktop nav + anchors
    ID_NAV_STATION_DESKTOP,
    ID_NAV_TIME_DESKTOP,
    ID_NAV_USER_DESKTOP,
    ID_NAV_DISPATCH_DESKTOP,
    ID_ANCHOR_STATION_NETWORK_DESKTOP,
    ID_ANCHOR_STATION_TRAFFIC_DESKTOP,
    ID_ANCHOR_STATION_FLOW_DESKTOP,
    ID_ANCHOR_TIME_HOURLY_DESKTOP,
    ID_ANCHOR_TIME_DAYHOUR_DESKTOP,
    ID_ANCHOR_TIME_DURATION_DESKTOP,
    ID_ANCHOR_USER_TYPE_DESKTOP,
    ID_ANCHOR_USER_DEMO_DESKTOP,
    ID_ANCHOR_USER_CROSSTAB_DESKTOP,
    ID_ANCHOR_DISPATCH_PLAN_DESKTOP,

    # Mobile nav + anchors
    ID_NAV_STATION_MOBILE,
    ID_NAV_TIME_MOBILE,
    ID_NAV_USER_MOBILE,
    ID_NAV_DISPATCH_MOBILE,
    ID_ANCHOR_STATION_NETWORK_MOBILE,
    ID_ANCHOR_STATION_TRAFFIC_MOBILE,
    ID_ANCHOR_STATION_FLOW_MOBILE,
    ID_ANCHOR_TIME_HOURLY_MOBILE,
    ID_ANCHOR_TIME_DAYHOUR_MOBILE,
    ID_ANCHOR_TIME_DURATION_MOBILE,
    ID_ANCHOR_USER_TYPE_MOBILE,
    ID_ANCHOR_USER_DEMO_MOBILE,
    ID_ANCHOR_USER_CROSSTAB_MOBILE,
    ID_ANCHOR_DISPATCH_PLAN_MOBILE,
)
from data_loader import (
    load_clean_data,
    load_gold_station_metrics,
    load_gold_top_routes,
    load_gold_top_destination,
)
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
from charts.time_analysis import (
    create_trips_by_hour_chart,
    create_day_hour_heatmap_chart,
    create_avg_duration_by_hour_chart,
    create_weekday_vs_weekend_duration_chart,
)
from charts.user_analysis import (
    create_user_type_distribution_chart,
    create_user_type_hour_chart,
    create_avg_duration_by_user_type_chart,
    create_age_group_distribution_chart,
    create_gender_distribution_chart,
    create_user_type_by_age_group_chart,
)
from components.station_inspector import render_station_inspector
from components.dispatch_panel import render_dispatch_panel

logger = logging.getLogger(__name__)


def _extract_station_name(click_data: dict | None) -> str | None:
    """Safely parse clicked station name from map scatter or horizontal bar chart."""
    if not click_data or "points" not in click_data or not click_data["points"]:
        return None
    pt = click_data["points"][0]

    cd = pt.get("customdata")
    if isinstance(cd, (list, tuple)) and len(cd) > 0:
        return str(cd[0])
    if isinstance(cd, str):
        return cd

    y_val = pt.get("y")
    if isinstance(y_val, str):
        return y_val

    return None


def register_callbacks(app: dash.Dash) -> None:
    """
    Register all Member 5 dashboard callbacks onto the Dash application instance.
    """

    # =======================================================================
    # SERVER-SIDE CALLBACKS (analytics – unchanged)
    # =======================================================================

    # -----------------------------------------------------------------------
    # 1. Main Dashboard Update
    # -----------------------------------------------------------------------
    @app.callback(
        [
            Output(ID_MAP, "figure"),
            Output(ID_TOP_STATIONS, "figure"),
            Output(ID_TOP_ROUTES, "figure"),
            Output(ID_FLOW_IMBALANCE, "figure"),
            Output(ID_ROUND_TRIP_CHART, "figure"),
            Output(ID_TRIPS_BY_HOUR, "figure"),
            Output(ID_DAY_HOUR_HEATMAP, "figure"),
            Output(ID_AVG_DURATION_BY_HOUR, "figure"),
            Output(ID_WEEKDAY_WEEKEND_DURATION, "figure"),
            Output(ID_USER_TYPE_DISTRIBUTION, "figure"),
            Output(ID_USER_TYPE_HOUR, "figure"),
            Output(ID_AVG_DURATION_BY_USER_TYPE, "figure"),
            Output(ID_AGE_GROUP_DISTRIBUTION, "figure"),
            Output(ID_GENDER_DISTRIBUTION, "figure"),
            Output(ID_USER_TYPE_BY_AGE_GROUP, "figure"),
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
        n = int(top_n) if top_n else 10
        user_filter = selected_user or "All"
        region_filter = selected_region or "All"
        show_flow_lines = "show" in (flow_lines_toggle or [])

        df = load_clean_data()

        if user_filter != "All" and "user_type" in df.columns:
            filtered_df = df[df["user_type"] == user_filter]
        else:
            filtered_df = df

        if user_filter == "All":
            station_metrics = load_gold_station_metrics()
        else:
            station_metrics = compute_canonical_station_metrics(filtered_df)

        if region_filter != "All":
            region_stns = set(
                station_metrics[station_metrics["region"] == region_filter]["station_name"]
            )
            station_metrics_view = station_metrics[station_metrics["region"] == region_filter]
            df_view = filtered_df[filtered_df["start_station_name"].isin(region_stns)]
        else:
            station_metrics_view = station_metrics
            df_view = filtered_df

        top_stations = compute_top_stations(station_metrics_view, top_n=n)

        if user_filter == "All" and region_filter == "All":
            top_routes = load_gold_top_routes().head(n)
        else:
            top_routes = compute_top_routes(df_view, top_n=n)

        flow_imbalance = compute_flow_imbalance(station_metrics_view, top_n=n)
        round_trips = compute_round_trip_hotspots(df_view, top_n=n)
        dispatch_pairs = compute_smart_dispatch_pairs(station_metrics_view, max_pairs=3)

        top_dest_map = {}

        if user_filter == "All" and region_filter == "All":
            gold_top_destination = load_gold_top_destination()

            if not gold_top_destination.empty:
                idx_max = (
                    gold_top_destination
                    .groupby("start_station_name")["trip_count"]
                    .idxmax()
                )

                top_pairs = gold_top_destination.loc[idx_max]

                top_dest_map = dict(
                    zip(
                        top_pairs["start_station_name"],
                        top_pairs["end_station_name"],
                    )
                )
        else:
            if not filtered_df.empty and "start_station_name" in filtered_df.columns:
                valid_trips = filtered_df[
                    (filtered_df["start_station_name"].notna())
                    & (filtered_df["end_station_name"].notna())
                    & (filtered_df["start_station_name"] != filtered_df["end_station_name"])
                ]

                if not valid_trips.empty:
                    dest_counts = (
                        valid_trips
                        .groupby(
                            ["start_station_name", "end_station_name"],
                            observed=True
                        )
                        .size()
                        .reset_index(name="cnt")
                    )

                    idx_max = (
                        dest_counts
                        .groupby("start_station_name", observed=True)["cnt"]
                        .idxmax()
                    )

                    top_pairs = dest_counts.loc[idx_max]

                    top_dest_map = dict(
                        zip(
                            top_pairs["start_station_name"],
                            top_pairs["end_station_name"],
                        )
                    )

        total_network_traffic = int(station_metrics_view["total_traffic"].sum()) if not station_metrics_view.empty else 0

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

        fig_trips_by_hour = create_trips_by_hour_chart(df_view)
        fig_day_hour_heatmap = create_day_hour_heatmap_chart(df_view)
        fig_avg_duration_by_hour = create_avg_duration_by_hour_chart(df_view)
        fig_weekday_weekend = create_weekday_vs_weekend_duration_chart(df_view)

        fig_user_type_distribution = create_user_type_distribution_chart(df_view)
        fig_user_type_hour = create_user_type_hour_chart(df_view)
        fig_avg_duration_by_user_type = create_avg_duration_by_user_type_chart(df_view)
        fig_age_group_distribution = create_age_group_distribution_chart(df_view)
        fig_gender_distribution = create_gender_distribution_chart(df_view)
        fig_user_type_by_age_group = create_user_type_by_age_group_chart(df_view)

        dispatch_children = render_dispatch_panel(dispatch_pairs)

        return (
            fig_map,
            fig_stations,
            fig_routes,
            fig_imbalance,
            fig_round_trip,
            fig_trips_by_hour,
            fig_day_hour_heatmap,
            fig_avg_duration_by_hour,
            fig_weekday_weekend,
            fig_user_type_distribution,
            fig_user_type_hour,
            fig_avg_duration_by_user_type,
            fig_age_group_distribution,
            fig_gender_distribution,
            fig_user_type_by_age_group,
            dispatch_children,
        )

    # -----------------------------------------------------------------------
    # 2. Station Selection Store
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
        triggered = ctx.triggered_id
        if triggered == ID_DRAWER_CLOSE_BTN:
            return None
        elif triggered == ID_MAP and map_click:
            return _extract_station_name(map_click)
        elif triggered == ID_TOP_STATIONS and bar_click:
            return _extract_station_name(bar_click)
        return dash.no_update

    # -----------------------------------------------------------------------
    # 3. Station Inspector
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
    # 4. CSV Export
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

        slug = reg.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        filename = f"fordgobike_station_metrics_{slug}.csv"
        return dcc.send_data_frame(metrics.to_csv, filename, index=False)

    # -----------------------------------------------------------------------
    # 5. Slider Badge
    # -----------------------------------------------------------------------
    @app.callback(
        Output("m5-slider-scope-badge", "children"),
        Input(ID_TOP_N_SLIDER, "value"),
    )
    def update_scope_badge(val):
        v = int(val) if val else 10
        return f"Top {v}"

    # =======================================================================
    # CLIENTSIDE CALLBACKS (sidebar navigation)
    # =======================================================================

    # -----------------------------------------------------------------------
    # C1. Nav button click → active section store
    # -----------------------------------------------------------------------
    clientside_callback(
        """
        function(n1, n2, n3, n4, n5, n6, n7, n8) {
            const ctx = dash_clientside.callback_context;
            if (!ctx || !ctx.triggered || ctx.triggered.length === 0) {
                return dash_clientside.no_update;
            }
            const triggerId = ctx.triggered_id;
            if (!triggerId) {
                return dash_clientside.no_update;
            }
            const sectionMap = {
                'm5-nav-station-desktop':  'station',
                'm5-nav-time-desktop':     'time',
                'm5-nav-user-desktop':     'user',
                'm5-nav-dispatch-desktop': 'dispatch',
                'm5-nav-station-mobile':   'station',
                'm5-nav-time-mobile':      'time',
                'm5-nav-user-mobile':      'user',
                'm5-nav-dispatch-mobile':  'dispatch'
            };
            return sectionMap[triggerId] || dash_clientside.no_update;
        }
        """,
        Output(ID_ACTIVE_SECTION_STORE, "data"),
        [
            Input(ID_NAV_STATION_DESKTOP, "n_clicks"),
            Input(ID_NAV_TIME_DESKTOP, "n_clicks"),
            Input(ID_NAV_USER_DESKTOP, "n_clicks"),
            Input(ID_NAV_DISPATCH_DESKTOP, "n_clicks"),
            Input(ID_NAV_STATION_MOBILE, "n_clicks"),
            Input(ID_NAV_TIME_MOBILE, "n_clicks"),
            Input(ID_NAV_USER_MOBILE, "n_clicks"),
            Input(ID_NAV_DISPATCH_MOBILE, "n_clicks"),
        ],
    )

    # -----------------------------------------------------------------------
    # C2. Active section → section visibility
    # -----------------------------------------------------------------------
    clientside_callback(
        """
        function(active_section) {
            const show = {display: 'block'};
            const hide = {display: 'none'};
            return [
                active_section === 'station'  ? show : hide,
                active_section === 'time'     ? show : hide,
                active_section === 'user'     ? show : hide,
                active_section === 'dispatch' ? show : hide
            ];
        }
        """,
        [
            Output(ID_SECTION_STATION, "style"),
            Output(ID_SECTION_TIME, "style"),
            Output(ID_SECTION_USER, "style"),
            Output(ID_SECTION_DISPATCH, "style"),
        ],
        Input(ID_ACTIVE_SECTION_STORE, "data"),
    )

    # -----------------------------------------------------------------------
    # C3. Active section → nav button active styling
    # -----------------------------------------------------------------------
    clientside_callback(
        """
        function(active_section) {
            const activeClass =
                'm5-nav-button m5-nav-button-active group w-full flex items-center gap-3 ' +
                'px-3 py-2.5 rounded-lg transition-colors duration-150 cursor-pointer ' +
                'text-left bg-teal-50 text-teal-700 border border-teal-200';
            const idleClass =
                'm5-nav-button group w-full flex items-center gap-3 px-3 py-2.5 ' +
                'rounded-lg transition-colors duration-150 cursor-pointer ' +
                'text-left text-slate-600 hover:bg-slate-100 hover:text-slate-900';
            function cls(key) {
                return key === active_section ? activeClass : idleClass;
            }
            return [
                cls('station'), cls('time'), cls('user'), cls('dispatch'),
                cls('station'), cls('time'), cls('user'), cls('dispatch')
            ];
        }
        """,
        [
            Output(ID_NAV_STATION_DESKTOP, "className"),
            Output(ID_NAV_TIME_DESKTOP, "className"),
            Output(ID_NAV_USER_DESKTOP, "className"),
            Output(ID_NAV_DISPATCH_DESKTOP, "className"),
            Output(ID_NAV_STATION_MOBILE, "className"),
            Output(ID_NAV_TIME_MOBILE, "className"),
            Output(ID_NAV_USER_MOBILE, "className"),
            Output(ID_NAV_DISPATCH_MOBILE, "className"),
        ],
        Input(ID_ACTIVE_SECTION_STORE, "data"),
    )

    # -----------------------------------------------------------------------
    # C4. Sub-link click → smooth scroll to the target group
    # -----------------------------------------------------------------------
    clientside_callback(
        """
        function(n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,
                 m1,m2,m3,m4,m5,m6,m7,m8,m9,m10) {
            const ctx = dash_clientside.callback_context;
            if (!ctx || !ctx.triggered || ctx.triggered.length === 0) {
                return dash_clientside.no_update;
            }
            const triggerId = ctx.triggered_id;
            if (!triggerId) {
                return dash_clientside.no_update;
            }
            const targetMap = {
                'm5-anchor-station-network-desktop': 'm5-anchor-station-network-group',
                'm5-anchor-station-traffic-desktop': 'm5-anchor-station-traffic-group',
                'm5-anchor-station-flow-desktop':    'm5-anchor-station-flow-group',
                'm5-anchor-station-network-mobile':  'm5-anchor-station-network-group',
                'm5-anchor-station-traffic-mobile':  'm5-anchor-station-traffic-group',
                'm5-anchor-station-flow-mobile':     'm5-anchor-station-flow-group',
                'm5-anchor-time-hourly-desktop':     'm5-anchor-time-hourly-group',
                'm5-anchor-time-dayhour-desktop':    'm5-anchor-time-dayhour-group',
                'm5-anchor-time-duration-desktop':   'm5-anchor-time-duration-group',
                'm5-anchor-time-hourly-mobile':      'm5-anchor-time-hourly-group',
                'm5-anchor-time-dayhour-mobile':     'm5-anchor-time-dayhour-group',
                'm5-anchor-time-duration-mobile':    'm5-anchor-time-duration-group',
                'm5-anchor-user-type-desktop':       'm5-anchor-user-type-group',
                'm5-anchor-user-demographics-desktop':'m5-anchor-user-demographics-group',
                'm5-anchor-user-crosstab-desktop':   'm5-anchor-user-crosstab-group',
                'm5-anchor-user-type-mobile':        'm5-anchor-user-type-group',
                'm5-anchor-user-demographics-mobile':'m5-anchor-user-demographics-group',
                'm5-anchor-user-crosstab-mobile':    'm5-anchor-user-crosstab-group',
                'm5-anchor-dispatch-plan-desktop':   'm5-anchor-dispatch-plan-group',
                'm5-anchor-dispatch-plan-mobile':    'm5-anchor-dispatch-plan-group'
            };
            const targetId = targetMap[triggerId];
            if (targetId) {
                const el = document.getElementById(targetId);
                if (el && el.scrollIntoView) {
                    el.scrollIntoView({behavior: 'smooth', block: 'start'});
                }
            }
            return triggerId;
        }
        """,
        Output(ID_ACTIVE_ANCHOR_STORE, "data"),
        [
            Input(ID_ANCHOR_STATION_NETWORK_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_STATION_TRAFFIC_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_STATION_FLOW_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_TIME_HOURLY_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_TIME_DAYHOUR_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_TIME_DURATION_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_USER_TYPE_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_USER_DEMO_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_USER_CROSSTAB_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_DISPATCH_PLAN_DESKTOP, "n_clicks"),
            Input(ID_ANCHOR_STATION_NETWORK_MOBILE, "n_clicks"),
            Input(ID_ANCHOR_STATION_TRAFFIC_MOBILE, "n_clicks"),
            Input(ID_ANCHOR_STATION_FLOW_MOBILE, "n_clicks"),
            Input(ID_ANCHOR_TIME_HOURLY_MOBILE, "n_clicks"),
            Input(ID_ANCHOR_TIME_DAYHOUR_MOBILE, "n_clicks"),
            Input(ID_ANCHOR_TIME_DURATION_MOBILE, "n_clicks"),
            Input(ID_ANCHOR_USER_TYPE_MOBILE, "n_clicks"),
            Input(ID_ANCHOR_USER_DEMO_MOBILE, "n_clicks"),
            Input(ID_ANCHOR_USER_CROSSTAB_MOBILE, "n_clicks"),
            Input(ID_ANCHOR_DISPATCH_PLAN_MOBILE, "n_clicks"),
        ],
    )

    # -----------------------------------------------------------------------
    # C5. Mobile drawer toggle
    # -----------------------------------------------------------------------
    clientside_callback(
        """
        function(toggle_n, backdrop_n, is_open) {
            const ctx = dash_clientside.callback_context;
            if (!ctx || !ctx.triggered || ctx.triggered.length === 0) {
                return dash_clientside.no_update;
            }
            const triggerId = ctx.triggered_id;
            if (triggerId === 'm5-mobile-menu-toggle') {
                return !is_open;
            }
            if (triggerId === 'm5-mobile-backdrop') {
                return false;
            }
            return dash_clientside.no_update;
        }
        """,
        Output(ID_MOBILE_MENU_STORE, "data"),
        [
            Input(ID_MOBILE_MENU_TOGGLE, "n_clicks"),
            Input(ID_MOBILE_BACKDROP, "n_clicks"),
        ],
        State(ID_MOBILE_MENU_STORE, "data"),
    )

    # -----------------------------------------------------------------------
    # C6. Mobile drawer + backdrop visibility
    # -----------------------------------------------------------------------
    clientside_callback(
        """
        function(is_open) {
            if (is_open) {
                return [
                    {'display': 'block'},
                    {'display': 'flex', 'flexDirection': 'column'}
                ];
            }
            return [
                {'display': 'none'},
                {'display': 'none'}
            ];
        }
        """,
        [
            Output(ID_MOBILE_BACKDROP, "style"),
            Output(ID_MOBILE_SIDEBAR, "style"),
        ],
        Input(ID_MOBILE_MENU_STORE, "data"),
    )

    # -----------------------------------------------------------------------
    # C7. Filter panel visibility — visible ONLY on Station Analysis
    # -----------------------------------------------------------------------
    clientside_callback(
        """
        function(active_section) {
            if (active_section === 'station') {
                return {'display': 'block'};
            }
            return {'display': 'none'};
        }
        """,
        Output(ID_FILTER_PANEL_WRAPPER, "style"),
        Input(ID_ACTIVE_SECTION_STORE, "data"),
    )