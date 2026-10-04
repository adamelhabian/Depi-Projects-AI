"""
components/navbar.py – Master Top Navigation Bar
================================================
Renders the top application header with active route breadcrumbs,
live cloud synchronization status, and quick-action toolbar.
"""

from __future__ import annotations

from dash import html, dcc
from config import NAV_ITEMS, ROUTE_OVERVIEW, ID_GLOBAL_EXPORT_BTN


def render_navbar(active_route: str = "/") -> html.Header:
    """
    Renders the top header bar matching the currently active page.
    """
    current_item = next((item for item in NAV_ITEMS if item["route"] == active_route), NAV_ITEMS[0])

    return html.Header(
        className="h-14 border-b border-slate-200 bg-white px-3 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-2xs w-full max-w-[100vw] overflow-hidden",
        children=[
            # Left: Sidebar Toggle Button + Route Breadcrumbs
            html.Div(
                className="flex items-center gap-2 sm:gap-3 text-xs text-slate-500 min-w-0 overflow-hidden",
                children=[
                    html.Button(
                        html.I(className="fas fa-bars text-sm text-slate-600"),
                        id="master-sidebar-toggle-btn",
                        className="p-2 rounded-lg hover:bg-slate-100 text-slate-600 hover:text-slate-900 transition-colors cursor-pointer border border-transparent hover:border-slate-200 focus:outline-none shrink-0",
                        title="Toggle Sidebar (Expand / Collapse)",
                        n_clicks=0,
                    ),
                    dcc.Link(
                        "Ford GoBike Analytics",
                        href=ROUTE_OVERVIEW,
                        className="font-bold sm:font-medium text-slate-900 sm:text-slate-700 hover:text-slate-800 transition-colors truncate",
                    ),
                    html.I(className="fas fa-chevron-right text-[10px] text-slate-400 hidden md:inline-block shrink-0"),
                    html.Span(
                        current_item["label"],
                        id="master-navbar-breadcrumb-label",
                        className="font-semibold text-slate-900 hidden md:inline-block truncate",
                    ),
                ],
            ),

            # Right: Live Badge & Export Quick Action
            html.Div(
                className="flex items-center gap-2 sm:gap-4 shrink-0",
                children=[
                    # Live Cloud Badge (Desktop & Tablet only)
                    html.Div(
                        className="hidden md:inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs font-medium text-slate-700",
                        children=[
                            html.Span(className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"),
                            html.Span("Supabase Cloud Active"),
                        ],
                    ),

                    # Export Button (Icon only on mobile, text on desktop)
                    html.Button(
                        [
                            html.I(className="fas fa-download text-xs md:mr-1.5"),
                            html.Span("Export Summary", className="hidden md:inline"),
                        ],
                        id=ID_GLOBAL_EXPORT_BTN,
                        className="flex items-center gap-1.5 p-2 md:px-3 md:py-1.5 rounded-lg bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer",
                        title="Export analytical summary report",
                        n_clicks=0,
                    ),

                    # Project GitHub Link
                    html.A(
                        html.I(className="fab fa-github text-slate-500 hover:text-slate-800 text-base transition-colors"),
                        href="https://github.com/adamelhabian/Depi-Projects-AI",
                        target="_blank",
                        title="Project Repository",
                        className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors",
                    ),
                ],
            ),
        ],
    )
