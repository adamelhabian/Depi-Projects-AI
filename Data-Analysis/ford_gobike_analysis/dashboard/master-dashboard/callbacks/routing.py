"""
callbacks/routing.py – Master Router Controller
===============================================
Coordinates URL routing, dynamic view rendering, active sidebar link styling,
and top navbar breadcrumbs synchronization.
"""

from __future__ import annotations

import logging
from dash import Input, Output, html

from config import (
    ID_URL,
    ID_PAGE_CONTENT,
    ROUTE_OVERVIEW,
    ROUTE_STATIONS,
    ROUTE_TIME_USER,
)
from pages.overview import render_overview_page
from pages.station_page import render_station_page
from pages.time_user_page import render_time_user_page
from components.navbar import render_navbar

logger = logging.getLogger(__name__)


def register_routing_callbacks(app) -> None:
    """Register URL routing and navigation state synchronization callbacks."""

    # 1. Page Content Router
    @app.callback(
        Output(ID_PAGE_CONTENT, "children"),
        Input(ID_URL, "pathname"),
    )
    def display_page(pathname: str | None):
        if not pathname:
            return render_overview_page()

        clean_path = pathname.rstrip("/")
        if not clean_path:
            clean_path = "/"

        if clean_path == ROUTE_STATIONS:
            return render_station_page()
        elif clean_path == ROUTE_TIME_USER:
            return render_time_user_page()
        elif clean_path in (ROUTE_OVERVIEW, "/overview"):
            return render_overview_page()
        else:
            # 404 / Fallback to Overview
            return html.Div(
                className="max-w-4xl mx-auto py-16 text-center",
                children=[
                    html.H2("Page Not Found", className="text-2xl font-bold text-slate-800 mb-2"),
                    html.P(f"No module route matches '{pathname}'.", className="text-slate-500 mb-6"),
                    render_overview_page(),
                ],
            )

    # 2. Synchronize Navbar Breadcrumb
    @app.callback(
        Output("master-navbar-container", "children"),
        Input(ID_URL, "pathname"),
    )
    def update_navbar_breadcrumb(pathname: str | None):
        path = pathname.rstrip("/") if pathname else "/"
        if not path:
            path = "/"
        return render_navbar(active_route=path)

    # 3. Synchronize Active Sidebar Links
    @app.callback(
        [
            Output("master-nav-nav-overview", "className"),
            Output("master-nav-nav-stations", "className"),
            Output("master-nav-nav-time-user", "className"),
        ],
        Input(ID_URL, "pathname"),
    )
    def update_sidebar_active_classes(pathname: str | None):
        path = pathname.rstrip("/") if pathname else "/"
        if not path:
            path = "/"

        def nav_class(target: str) -> str:
            is_active = (path == target) or (target == ROUTE_OVERVIEW and path in ("/", "/overview"))
            base = "group flex items-center justify-between px-3.5 py-3 rounded-xl transition-all duration-200 text-sm "
            if is_active:
                return base + "active bg-slate-800/90 text-white font-semibold shadow-sm border border-slate-700/80"
            return base + "text-slate-400 hover:text-slate-100 hover:bg-slate-800/50"

        return [
            nav_class(ROUTE_OVERVIEW),
            nav_class(ROUTE_STATIONS),
            nav_class(ROUTE_TIME_USER),
        ]
