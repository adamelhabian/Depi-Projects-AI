"""
layout.py – Master Shell Layout
===============================
Top-level application shell coordinating responsive sidebar navigation,
sticky top navbar, and dynamic page container with loading state.
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
    Main content has a left offset equal to the sidebar width (w-72 = 288px).
    """
    return html.Div(
        className="min-h-screen bg-slate-50 antialiased text-slate-800",
        children=[
            # 1. URL Router
            dcc.Location(id=ID_URL, refresh=False),

            # 2. Fixed Sidebar – always visible regardless of scroll position
            render_sidebar(active_route="/"),

            # 3. Main Content Area – offset from the fixed sidebar (288px = w-72)
            html.Div(
                # ml-72 gives 288px left margin matching the fixed sidebar width.
                # On small screens (< md) the sidebar is hidden so we remove the margin.
                style={"marginLeft": "288px"},
                className="flex flex-col min-h-screen bg-slate-50",
                children=[
                    # Sticky Top Navbar
                    html.Div(
                        id="master-navbar-container",
                        children=render_navbar(active_route="/"),
                    ),

                    # ── Global Filter Bar (persists across all pages) ──────
                    render_global_filter_bar(),

                    # Dynamic Page Content with Loading Spinner
                    html.Div(
                        className="flex-1",
                        children=[
                            dcc.Loading(
                                id="master-page-loading",
                                type="circle",
                                color="#6366F1",
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
