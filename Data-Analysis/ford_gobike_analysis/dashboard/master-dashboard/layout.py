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


def create_master_layout() -> html.Div:
    """
    Renders the master application shell layout.
    """
    return html.Div(
        className="min-h-screen bg-slate-50 flex flex-col antialiased text-slate-800",
        children=[
            # 1. URL Router
            dcc.Location(id=ID_URL, refresh=False),

            # 2. Outer Layout Shell: Sidebar + Main Content Area
            html.Div(
                className="flex-1 flex flex-col md:flex-row min-h-screen",
                children=[
                    # Left Navigation Sidebar
                    render_sidebar(active_route="/"),

                    # Right Main Content Workspace
                    html.Main(
                        className="flex-1 flex flex-col bg-slate-50 min-w-0 overflow-x-hidden",
                        children=[
                            # Top Navbar
                            html.Div(
                                id="master-navbar-container",
                                children=render_navbar(active_route="/"),
                            ),

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
            ),
        ],
    )
