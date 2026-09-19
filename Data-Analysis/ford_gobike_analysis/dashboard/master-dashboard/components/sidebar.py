"""
components/sidebar.py – Executive Navigation Sidebar
====================================================
Renders the primary navigation sidebar for the Master Analytics Platform,
featuring brand identity, navigation routes, active highlights, and live Supabase status.
"""

from __future__ import annotations

from dash import html, dcc
from config import NAV_ITEMS, ID_SIDEBAR, ID_DB_STATUS


def render_sidebar(active_route: str = "/") -> html.Aside:
    """
    Renders the responsive sidebar navigation component.
    """
    nav_links = []
    for item in NAV_ITEMS:
        is_active = (active_route == item["route"])
        active_class = "active bg-slate-800/90 text-white font-semibold shadow-sm border border-slate-700/80" if is_active else "text-slate-400 hover:text-slate-100 hover:bg-slate-800/50"
        indicator = html.Span(className="w-1.5 h-6 rounded-full bg-emerald-400 mr-2") if is_active else None

        link = dcc.Link(
            id=f"master-nav-{item['id']}",
            href=item["route"],
            className=f"group flex items-center justify-between px-3.5 py-3 rounded-xl transition-all duration-200 text-sm {active_class}",
            children=[
                html.Div(
                    className="flex items-center gap-3",
                    children=[
                        indicator if is_active else html.Span(className="w-1.5 h-6 mr-2 opacity-0"),
                        html.I(className=f"{item['icon']} text-base group-hover:scale-110 transition-transform"),
                        html.Span(item["label"], className="tracking-wide"),
                    ],
                ),
                html.Span(
                    item["badge"],
                    className=f"text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full {item['badge_color']}",
                ),
            ],
        )
        nav_links.append(link)

    return html.Aside(
        id=ID_SIDEBAR,
        className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-5 min-h-screen select-none",
        children=[
            # Top Section: Brand & Navigation
            html.Div(
                children=[
                    # Brand Header
                    html.Div(
                        className="flex items-center gap-3 px-2 pb-6 mb-6 border-b border-slate-800/80",
                        children=[
                            html.Div(
                                className="w-11 h-11 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20",
                                children=[
                                    html.I(className="fas fa-bicycle text-xl"),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.H1(
                                        "Ford GoBike",
                                        className="text-lg font-extrabold text-white tracking-tight leading-none",
                                    ),
                                    html.Span(
                                        "Master Analytics Platform",
                                        className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase",
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Navigation Header Label
                    html.Div(
                        className="px-3 pb-2 text-[10px] font-bold uppercase tracking-widest text-slate-500",
                        children="Navigation Modules",
                    ),

                    # Navigation Links Container
                    html.Nav(
                        className="flex flex-col gap-1.5",
                        children=nav_links,
                    ),
                ],
            ),

            # Bottom Section: Cloud Database Status Badge & Metadata
            html.Div(
                className="pt-5 border-t border-slate-800/80",
                children=[
                    html.Div(
                        id=ID_DB_STATUS,
                        className="bg-slate-800/60 rounded-xl p-3.5 border border-slate-700/50",
                        children=[
                            html.Div(
                                className="flex items-center justify-between mb-1",
                                children=[
                                    html.Span(
                                        "Data Warehouse",
                                        className="text-xs font-semibold text-slate-300",
                                    ),
                                    html.Div(
                                        className="flex items-center gap-1.5",
                                        children=[
                                            html.Span(className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"),
                                            html.Span(
                                                "Connected",
                                                className="text-[11px] font-bold text-emerald-400",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                "Supabase PostgreSQL · Gold Layer",
                                className="text-[11px] text-slate-400 font-mono truncate",
                            ),
                        ],
                    ),
                    html.Div(
                        className="text-center text-[10px] text-slate-500 mt-3",
                        children="DEPI BI Final Project · Multi-Module Suite",
                    ),
                ],
            ),
        ],
    )
