"""
components/navbar.py – Master Top Navigation Bar
================================================
Renders the top application header with active route breadcrumbs,
live cloud synchronization status, and quick-action toolbar.
"""

from __future__ import annotations

from dash import html, dcc
from config import NAV_ITEMS, ROUTE_OVERVIEW


def render_navbar(active_route: str = "/") -> html.Header:
    """
    Renders the top header bar matching the currently active page.
    """
    current_item = next((item for item in NAV_ITEMS if item["route"] == active_route), NAV_ITEMS[0])

    return html.Header(
        className="bg-white border-b border-slate-200/80 px-6 py-4 sticky top-0 z-30 flex items-center justify-between shadow-xs",
        children=[
            # Left: Route Breadcrumbs & Section Title
            html.Div(
                className="flex items-center gap-3",
                children=[
                    html.Div(
                        className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider",
                        children=[
                            dcc.Link("Platform", href=ROUTE_OVERVIEW, className="hover:text-indigo-600 transition-colors"),
                            html.Span("/"),
                            html.Span(current_item["label"], className="text-slate-800 font-bold"),
                        ],
                    ),
                    html.Span(
                        current_item["badge"],
                        className=f"text-[10px] font-bold px-2.5 py-0.5 rounded-full {current_item['badge_color']} hidden sm:inline-block",
                    ),
                ],
            ),

            # Right: Cloud Sync Status & Quick Links
            html.Div(
                className="flex items-center gap-4",
                children=[
                    # Live Cloud Badge
                    html.Div(
                        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs font-medium text-slate-700",
                        children=[
                            html.Span(className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"),
                            html.Span("Supabase Cloud Active"),
                        ],
                    ),

                    # Quick Link to Standalone Modules
                    html.Div(
                        className="flex items-center gap-2",
                        children=[
                            html.A(
                                html.I(className="fab fa-github text-slate-500 hover:text-slate-800 text-lg transition-colors"),
                                href="https://github.com/adamelhabian/Depi-Projects-AI",
                                target="_blank",
                                title="Project Repository",
                                className="p-2 rounded-lg hover:bg-slate-100 transition-colors",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
