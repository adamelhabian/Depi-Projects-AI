"""
callbacks/routing.py – Master Router Controller
===============================================
Coordinates URL routing, dynamic view rendering, active sidebar link styling,
and top navbar breadcrumbs synchronization.
"""

from __future__ import annotations

import logging
from dash import Input, Output, State, html, no_update
import dash

from config import (
    ID_URL,
    ID_PAGE_CONTENT,
    ID_SIDEBAR,
    NAV_ITEMS,
    ROUTE_OVERVIEW,
    ROUTE_STATIONS,
    ROUTE_TIME_USER,
    ROUTE_USER_TRIPS,
)
from pages.overview import render_overview_page
from pages.station_page import render_station_page
from pages.time_user_page import render_time_user_page
from pages.user_trips_page import render_user_trips_page
from components.navbar import render_navbar

logger = logging.getLogger(__name__)


def _skeleton_page(label: str = "Loading module…") -> html.Div:
    """
    Shimmer placeholder shown immediately while the module data loads.
    Uses the .skeleton CSS classes defined in master_style.css.
    """
    return html.Div(
        className="skeleton-page",
        children=[
            # Label
            html.Div(
                className="flex items-center gap-3 mb-2",
                children=[
                    html.Div(className="skeleton skeleton-line skeleton-line-short"),
                    html.Span(label, className="text-slate-400 text-sm animate-pulse"),
                ],
            ),
            # 4 KPI card skeletons
            html.Div(
                className="skeleton-kpi-row",
                children=[html.Div(className="skeleton skeleton-kpi") for _ in range(4)],
            ),
            # 2 chart row
            html.Div(
                className="skeleton-chart-row",
                children=[html.Div(className="skeleton skeleton-chart") for _ in range(2)],
            ),
            # 1 wide chart
            html.Div(className="skeleton skeleton-chart"),
        ],
    )


def _error_page(message: str) -> html.Div:
    """Friendly error card shown when a page fails to render."""
    return html.Div(
        className="max-w-lg mx-auto mt-24 p-8 bg-white rounded-2xl border border-rose-100 shadow-sm text-center",
        children=[
            html.Div("⚠️", className="text-4xl mb-3"),
            html.H3("Something went wrong", className="text-lg font-bold text-slate-800 mb-2"),
            html.P(message, className="text-slate-500 text-sm leading-relaxed"),
            html.P(
                "Try refreshing the page. If the problem persists, check the Supabase connection.",
                className="text-slate-400 text-xs mt-2",
            ),
        ],
    )


def register_routing_callbacks(app) -> None:
    """Register URL routing and navigation state synchronization callbacks."""

    # 1. Page Content Router
    @app.callback(
        Output(ID_PAGE_CONTENT, "children"),
        Input(ID_URL, "pathname"),
    )
    def display_page(pathname: str | None):
        if not pathname:
            try:
                return render_overview_page()
            except Exception as exc:
                logger.exception("Overview render failed: %s", exc)
                return _error_page(str(exc))

        clean_path = pathname.rstrip("/")
        if not clean_path:
            clean_path = "/"

        try:
            if clean_path == ROUTE_STATIONS:
                return render_station_page()
            elif clean_path == ROUTE_TIME_USER:
                return render_time_user_page()
            elif clean_path == ROUTE_USER_TRIPS:
                return render_user_trips_page()
            elif clean_path in (ROUTE_OVERVIEW, "/overview"):
                return render_overview_page()
            else:
                # 404 / Fallback
                return html.Div(
                    className="max-w-4xl mx-auto py-16 text-center",
                    children=[
                        html.H2("Page Not Found", className="text-2xl font-bold text-slate-800 mb-2"),
                        html.P(f"No module route matches '{pathname}'.", className="text-slate-500 mb-6"),
                        render_overview_page(),
                    ],
                )
        except Exception as exc:
            logger.exception("Page render failed for '%s': %s", pathname, exc)
            return _error_page(str(exc))

    # 2. Synchronize Navbar Breadcrumb (without re-rendering entire navbar)
    @app.callback(
        Output("master-navbar-breadcrumb-label", "children"),
        Input(ID_URL, "pathname"),
    )
    def update_navbar_breadcrumb(pathname: str | None):
        path = pathname.rstrip("/") if pathname else "/"
        if not path:
            path = "/"
        current_item = next((item for item in NAV_ITEMS if item["route"] == path), NAV_ITEMS[0])
        return current_item["label"]

    # 3. Synchronize Active Sidebar Links (All 4 modules)
    @app.callback(
        [
            Output("master-nav-nav-overview", "className"),
            Output("master-nav-nav-stations", "className"),
            Output("master-nav-nav-time-user", "className"),
            Output("master-nav-nav-user-trips", "className"),
        ],
        Input(ID_URL, "pathname"),
    )
    def update_sidebar_active_classes(pathname: str | None):
        path = pathname.rstrip("/") if pathname else "/"
        if not path:
            path = "/"

        def nav_class(target: str) -> str:
            is_active = (path == target) or (target == ROUTE_OVERVIEW and path in ("/", "/overview"))
            base = "sidebar-nav-item group flex items-center gap-3 px-3.5 py-2.5 rounded-lg transition-all duration-150 text-[13px] "
            if is_active:
                return base + "active text-teal-400 font-semibold bg-teal-500/15 border-r-2 border-teal-400"
            return base + "text-slate-400 hover:text-slate-100 hover:bg-white/[0.04]"

        return [
            nav_class(ROUTE_OVERVIEW),
            nav_class(ROUTE_STATIONS),
            nav_class(ROUTE_TIME_USER),
            nav_class(ROUTE_USER_TRIPS),
        ]

    # 4. Interactive Collapsible Navigation Sidebar & Mobile Drawer
    # 4a. Mobile Navigation Drawer State
    @app.callback(
        Output("master-mobile-drawer-open-store", "data"),
        [
            Input("master-sidebar-toggle-btn", "n_clicks"),
            Input("master-sidebar-close-btn", "n_clicks"),
            Input("master-sidebar-backdrop", "n_clicks"),
            Input(ID_URL, "pathname"),
        ],
        State("master-mobile-drawer-open-store", "data"),
        prevent_initial_call=True,
    )
    def handle_mobile_drawer_state(toggle_clicks, close_clicks, backdrop_clicks, pathname, is_open):
        """Toggle or close mobile drawer on button click, backdrop click, or route navigation."""
        trigger = dash.ctx.triggered_id
        if trigger == "master-sidebar-toggle-btn":
            return not bool(is_open)
        # Any of close button, backdrop click, or route navigation closes the mobile drawer
        return False

    # 4b. Desktop Collapsible Navigation Sidebar
    @app.callback(
        Output("master-sidebar-collapsed-store", "data"),
        [
            Input("master-sidebar-toggle-btn", "n_clicks"),
            Input("master-sidebar-close-btn", "n_clicks"),
        ],
        State("master-sidebar-collapsed-store", "data"),
        prevent_initial_call=True,
    )
    def toggle_desktop_sidebar(toggle_clicks, close_clicks, is_collapsed):
        """User explicitly clicked toggle or close button to change desktop sidebar state."""
        return not bool(is_collapsed)

    # 4c. Synchronize visual CSS classes for sidebar, main wrapper, and backdrop
    @app.callback(
        [
            Output(ID_SIDEBAR, "className"),
            Output("master-main-wrapper", "className"),
            Output("master-sidebar-backdrop", "className"),
        ],
        [
            Input("master-sidebar-collapsed-store", "data"),
            Input("master-mobile-drawer-open-store", "data"),
        ],
    )
    def apply_sidebar_visual_state(is_desktop_collapsed, is_mobile_open):
        """Ensure sidebar open/closed state persists across page navigation and tabs."""
        base_sidebar = "w-64 bg-[#0B1329] border-r border-slate-800 flex flex-col justify-between p-5 select-none"
        base_main = "flex flex-col min-h-screen bg-slate-50"
        base_backdrop = "master-sidebar-backdrop fixed inset-0 bg-slate-950/60 backdrop-blur-xs z-[9990] transition-opacity duration-300"

        sidebar_classes = [base_sidebar]
        main_classes = [base_main]

        if is_desktop_collapsed:
            sidebar_classes.append("sidebar-collapsed")
            main_classes.append("sidebar-collapsed")

        if is_mobile_open:
            sidebar_classes.append("sidebar-mobile-open")
            backdrop_class = f"{base_backdrop} block opacity-100 pointer-events-auto"
        else:
            backdrop_class = f"{base_backdrop} hidden opacity-0 pointer-events-none"

        return " ".join(sidebar_classes), " ".join(main_classes), backdrop_class


