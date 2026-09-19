"""
components/sidebar.py – Executive Navigation Sidebar
====================================================
Fixed left navigation sidebar styled with Dark Navy (#0B1329),
featuring:
  - Brand identity: "Ford GoBike" + "ANALYTICS PLATFORM" in small caps
  - Navigation items with icons, badges, active highlights, and route links
  - Live indicator: "Data Warehouse Connected" with pulsing green dot
  - Quick stats pill: Total Trips: 174,724 | Stations: 329
"""

from __future__ import annotations

from dash import html, dcc
from config import NAV_ITEMS, ID_SIDEBAR, ID_DB_STATUS


def render_sidebar(active_route: str = "/") -> html.Aside:
    """
    Renders the fixed modern SaaS sidebar (w-64, #0B1329).
    """
    nav_links = []
    for item in NAV_ITEMS:
        is_active = (active_route == item["route"]) or (active_route == "/overview" and item["route"] == "/")
        active_class = (
            "bg-teal-500/15 text-teal-400 font-semibold border-r-2 border-teal-400 shadow-sm"
            if is_active
            else "text-slate-400 hover:text-slate-100 hover:bg-white/[0.04]"
        )

        link = dcc.Link(
            id=f"master-nav-{item['id']}",
            href=item["route"],
            className=f"group flex items-center justify-between px-3.5 py-2.5 rounded-lg transition-all duration-150 text-sm {active_class}",
            children=[
                html.Div(
                    className="flex items-center gap-3",
                    children=[
                        html.I(className=f"{item['icon']} text-base group-hover:scale-105 transition-transform"),
                        html.Span(item["label"], className="tracking-wide text-xs font-medium"),
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
        className="w-64 bg-[#0B1329] border-r border-slate-800 flex flex-col justify-between p-5 select-none text-slate-100",
        style={
            "position": "fixed",
            "top": "0",
            "left": "0",
            "height": "100vh",
            "width": "16rem",  # 256px = w-64
            "overflowY": "auto",
            "zIndex": "40",
        },
        children=[
            # Top Section: Brand & Navigation
            html.Div(
                children=[
                    # Brand Header
                    html.Div(
                        className="flex items-center gap-3 px-1 pb-5 mb-5 border-b border-slate-800/80",
                        children=[
                            html.Div(
                                className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 via-teal-400 to-indigo-500 flex items-center justify-center text-slate-950 shadow-md shadow-teal-500/20",
                                children=[
                                    html.I(className="fas fa-bicycle text-lg"),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.H1(
                                        "Ford GoBike",
                                        className="text-base font-bold text-white tracking-tight leading-tight",
                                    ),
                                    html.Span(
                                        "ANALYTICS PLATFORM",
                                        className="text-[9px] font-semibold tracking-widest text-teal-400 uppercase",
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Navigation Header Label
                    html.Div(
                        className="px-2 pb-2 text-[10px] font-bold uppercase tracking-widest text-slate-400",
                        children="Analytics Modules",
                    ),

                    # Navigation Links Container
                    html.Nav(
                        className="flex flex-col gap-1",
                        children=nav_links,
                    ),
                ],
            ),

            # Bottom Section: Live Indicator & Quick Stats Pill
            html.Div(
                className="pt-4 border-t border-slate-800/80 flex flex-col gap-3",
                children=[
                    # Live Indicator
                    html.Div(
                        id=ID_DB_STATUS,
                        className="bg-slate-900/90 rounded-xl p-3 border border-slate-800",
                        children=[
                            html.Div(
                                className="flex items-center justify-between",
                                children=[
                                    html.Span(
                                        "Data Warehouse",
                                        className="text-xs font-medium text-slate-300",
                                    ),
                                    html.Div(
                                        className="flex items-center gap-1.5",
                                        children=[
                                            html.Span(
                                                className="relative flex h-2 w-2",
                                                children=[
                                                    html.Span(className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"),
                                                    html.Span(className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"),
                                                ],
                                            ),
                                            html.Span(
                                                "Connected",
                                                className="text-[11px] font-bold text-emerald-400",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                "Supabase Cloud · gold.trip_analytics",
                                className="text-[10px] text-slate-400 font-mono truncate mt-1",
                            ),
                        ],
                    ),

                    # Quick Stats Pill
                    html.Div(
                        className="bg-slate-900/60 rounded-lg px-3 py-2 border border-slate-800/60 text-center",
                        children=[
                            html.Div(
                                [
                                    html.Span("174,724", className="font-semibold text-white"),
                                    html.Span(" Trips · ", className="text-slate-400"),
                                    html.Span("329", className="font-semibold text-white"),
                                    html.Span(" Stations", className="text-slate-400"),
                                ],
                                className="text-[11px] text-slate-300",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
