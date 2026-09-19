"""
layout.py – Master Shell Layout
===============================
Top-level application shell coordinating:
  - Fixed left sidebar (w-64 = 256px, #0B1329)
  - Sticky top navbar with active route breadcrumbs
  - Sticky global filter bar with session dcc.Store
  - Dynamic page container with loading indicator
  - Executive application footer
"""

from __future__ import annotations

from dash import html, dcc
from config import ID_URL, ID_PAGE_CONTENT
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
        className="min-h-screen bg-slate-50 antialiased text-slate-800",
        children=[
            # 1. URL Router
            dcc.Location(id=ID_URL, refresh=False),

            # 2. Fixed Sidebar – always visible regardless of scroll position
            render_sidebar(active_route="/"),

            # 3. Main Content Area – offset from the fixed sidebar (w-64 = 256px)
            html.Div(
                style={"marginLeft": "16rem"},
                className="flex flex-col min-h-screen bg-slate-50",
                children=[
                    # Sticky Top Navbar
                    html.Div(
                        id="master-navbar-container",
                        children=render_navbar(active_route="/"),
                    ),

                    # Global Filter Bar (persists across all pages via dcc.Store)
                    render_global_filter_bar(),

                    # Dynamic Page Content with Loading Spinner
                    html.Div(
                        className="flex-1",
                        children=[
                            dcc.Loading(
                                id="master-page-loading",
                                type="dot",
                                color="#14B8A6",
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
