"""
callbacks/station_callbacks.py – Station & Network Flow Callbacks
==================================================================
Handles:
  1. Map marker click -> updates Station Profile Drawer with live dock info
  2. Top-N slider & Corridor toggle -> updates horizontal bar charts and map layers
  3. Rebalancing CSV export button -> downloads dispatch plan via dcc.Download
"""

from __future__ import annotations

import pandas as pd
from dash import Input, Output, State, dcc, no_update
from config import (
    ID_STATION_TOPN_SLIDER,
    ID_STATION_CORRIDOR_TOGGLE,
    ID_STATION_MAP,
    ID_STATION_DRAWER_CONTENT,
    ID_STATION_CHART_BUSIEST,
    ID_STATION_CHART_DEFICIT,
    ID_STATION_CHART_SURPLUS,
    ID_STATION_CHART_LOOPS,
    ID_STATION_REBALANCING_DOWNLOAD_BTN,
    ID_STATION_REBALANCING_DOWNLOAD,
)
from pages.station_page import (
    render_station_drawer,
    build_busiest_stations_figure,
    build_deficit_stations_figure,
    build_surplus_stations_figure,
    build_loops_stations_figure,
    build_station_map_figure,
)
from data_loader import load_station_analytics_data


def register_station_callbacks(app) -> None:
    """Registers reactive callbacks for the Station & Network Flow view."""

    # 1. Map Marker Click -> Populate Station Profile Drawer
    @app.callback(
        Output(ID_STATION_DRAWER_CONTENT, "children"),
        Input(ID_STATION_MAP, "clickData"),
        prevent_initial_call=True,
    )
    def handle_station_click(click_data):
        if not click_data or "points" not in click_data:
            return no_update

        point = click_data["points"][0]
        # Customdata contains [name, region, total_flow, net_flow, capacity, loop_ratio]
        customdata = point.get("customdata")
        if customdata and len(customdata) >= 6:
            station_info = {
                "name": customdata[0],
                "region": customdata[1],
                "total_flow": customdata[2],
                "net_flow": customdata[3],
                "capacity": customdata[4],
                "loop_ratio": customdata[5],
            }
            return render_station_drawer(station_info)

        return no_update

    # 2. Top-N Slider -> Update the 4 Horizontal Bar Charts
    @app.callback(
        [
            Output(ID_STATION_CHART_BUSIEST, "figure"),
            Output(ID_STATION_CHART_DEFICIT, "figure"),
            Output(ID_STATION_CHART_SURPLUS, "figure"),
            Output(ID_STATION_CHART_LOOPS, "figure"),
        ],
        Input(ID_STATION_TOPN_SLIDER, "value"),
    )
    def update_bar_charts_top_n(top_n: int | None):
        n = top_n if top_n and top_n >= 5 else 10
        data = load_station_analytics_data()
        stns_df = data.get("stations_df", pd.DataFrame())

        return [
            build_busiest_stations_figure(stns_df, top_n=n),
            build_deficit_stations_figure(stns_df, top_n=n),
            build_surplus_stations_figure(stns_df, top_n=n),
            build_loops_stations_figure(stns_df, top_n=n),
        ]

    # 3. Corridor Lines Toggle -> Update Map Figure
    @app.callback(
        Output(ID_STATION_MAP, "figure"),
        Input(ID_STATION_CORRIDOR_TOGGLE, "value"),
        prevent_initial_call=True,
    )
    def toggle_transit_corridors(corridor_value):
        show = "SHOW" in (corridor_value or [])
        data = load_station_analytics_data()
        stns_df = data.get("stations_df", pd.DataFrame())
        corridors = data.get("corridors", [])
        return build_station_map_figure(stns_df, corridors, show_corridors=show)

    # 4. Rebalancing CSV Download
    @app.callback(
        Output(ID_STATION_REBALANCING_DOWNLOAD, "data"),
        Input(ID_STATION_REBALANCING_DOWNLOAD_BTN, "n_clicks"),
        prevent_initial_call=True,
    )
    def export_rebalancing_csv(n_clicks):
        if not n_clicks:
            return no_update

        data = load_station_analytics_data()
        rebal_list = data.get("rebalancing", [])
        if not rebal_list:
            return no_update

        export_df = pd.DataFrame(rebal_list)[[
            "rank", "priority", "region", "surplus_station", "surplus_net",
            "deficit_station", "deficit_net", "distance_km", "transfer_bikes"
        ]]
        return dcc.send_data_frame(export_df.to_csv, "ford_gobike_fleet_rebalancing_plan.csv", index=False)
