"""
layout.py – Master Shell Layout
===============================
Top-level application shell coordinating responsive sidebar navigation,
sticky top navbar, and dynamic page container with loading state.
"""

from __future__ import annotations

from dash import html, dcc
from config import ID_URL, ID_PAGE_CONTENT, ID_GLOBAL_DOWNLOAD_EXPORT
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.footer import render_footer
from components.global_filter_bar import render_global_filter_bar


def create_master_layout() -> html.Div:
    """
    Renders the master application shell layout.
    Sidebar is position:fixed (never scrolls away).
    Main content has a left offset equal to the sidebar width (w-64 = 16rem = 256px).
    """
    return html.Div(
        id="master-root-container",
        className="min-h-screen bg-slate-50 antialiased text-slate-800",
        children=[
            # 1. URL Router, Global File Downloader & Sidebar Collapsed Store
            dcc.Location(id=ID_URL, refresh=False),
            dcc.Download(id=ID_GLOBAL_DOWNLOAD_EXPORT),
            dcc.Store(id="master-sidebar-collapsed-store", data=False, storage_type="local"),

            # 2. Fixed Sidebar – always visible regardless of scroll position
            render_sidebar(active_route="/"),

            # 3. Main Content Area – offset from the fixed sidebar (w-64 = 256px)
            html.Div(
                id="master-main-wrapper",
                style={"marginLeft": "16rem", "width": "calc(100% - 16rem)", "minHeight": "100vh", "overflowX": "hidden"},
                className="flex flex-col min-h-screen bg-slate-50",
                children=[
                    # Sticky Top Navbar
                    html.Div(
                        id="master-navbar-container",
                        children=render_navbar(active_route="/"),
                    ),

                    # ── Global Filter Bar (persists across all pages) ──────
                    render_global_filter_bar(),

                    # Dynamic Page Content – wrapped in dcc.Loading so a skeleton
                    # spinner shows immediately on navigation, replacing the old
                    # page content before new content arrives (eliminates the
                    # ~9s "stale page visible" problem observed on /user-trips).
                    html.Div(
                        className="flex-1",
                        children=[
                            dcc.Loading(
                                id="master-page-loading",
                                type="circle",
                                color="#14B8A6",
                                overlay_style={
                                    "visibility": "visible",
                                    "opacity": 0.5,
                                    "backgroundColor": "#F8FAFC",
                                },
                                children=html.Div(id=ID_PAGE_CONTENT),
                            ),
                        ],
                    ),

                    # Application Footer
                    render_footer(),
                ],
            ),
        ],
    )
