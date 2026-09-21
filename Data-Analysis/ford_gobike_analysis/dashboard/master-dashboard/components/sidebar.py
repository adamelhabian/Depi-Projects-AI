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
    Renders the ultra-modern SaaS responsive sidebar navigation component.
    """
    nav_links = []
    for item in NAV_ITEMS:
        is_active = (active_route == item["route"]) or (active_route == "/overview" and item["route"] == "/")
        if is_active:
            active_class = "sidebar-nav-item active text-teal-400 font-semibold bg-teal-500/15 border-r-2 border-teal-400"
            icon_style = "text-teal-400"
        else:
            active_class = "sidebar-nav-item text-slate-400 hover:text-slate-100 hover:bg-white/[0.04]"
            icon_style = "text-slate-400 group-hover:text-slate-200"

        link = dcc.Link(
            id=f"master-nav-{item['id']}",
            href=item["route"],
            className=f"group flex items-center gap-3 px-3.5 py-2.5 rounded-lg transition-all duration-150 text-[13px] {active_class}",
            children=[
                html.Div(
                    className=f"w-6 h-6 rounded-md flex items-center justify-center {icon_style} transition-colors",
                    children=[html.I(className=f"{item['icon']} text-sm group-hover:scale-110 transition-transform")],
                ),
                html.Span(item["label"], className="tracking-wide font-medium"),
            ],
        )
        nav_links.append(link)

    return html.Aside(
        id=ID_SIDEBAR,
        className="w-64 bg-[#0B1329] border-r border-slate-800 flex flex-col justify-between p-5 select-none",
        style={
            "position": "fixed",
            "top": "0",
            "left": "0",
            "height": "100vh",
            "overflowY": "auto",
            "zIndex": "40",
        },
        children=[
            # Top Section: Brand & Navigation
            html.Div(
                children=[
                    # Brand Header
                    html.Div(
                        className="flex items-center justify-between px-2 pb-5 mb-5 border-b border-slate-800",
                        children=[
                            html.Div(
                                className="flex items-center gap-3",
                                children=[
                                    html.Div(
                                        className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-indigo-500 flex items-center justify-center text-slate-950 shadow-md shadow-teal-500/20",
                                        children=[
                                            html.I(className="fas fa-bicycle text-lg text-slate-950"),
                                        ],
                                    ),
                                    html.Div(
                                        children=[
                                            html.H1(
                                                "Ford GoBike",
                                                className="text-sm font-bold text-white tracking-tight leading-tight",
                                            ),
                                            html.Span(
                                                "ANALYTICS PLATFORM",
                                                className="text-[9px] font-semibold tracking-widest text-teal-400 uppercase block mt-0.5",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Button(
                                html.I(className="fas fa-angles-left text-xs text-slate-400 hover:text-white"),
                                id="master-sidebar-close-btn",
                                className="p-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer border border-slate-700/50",
                                title="Collapse Sidebar",
                                n_clicks=0,
                            ),
                        ],
                    ),

                    # Section Header
                    html.Div(
                        className="px-3 pb-2 text-[10px] font-bold uppercase tracking-widest text-slate-400",
                        children="Analytics Modules",
                    ),

                    # Navigation Links Container
                    html.Nav(
                        className="flex flex-col gap-1",
                        children=nav_links,
                    ),
                ],
            ),

            # Bottom Section: Live Warehouse Connection Status
            html.Div(
                className="pt-3 border-t border-slate-800 flex flex-col gap-2",
                children=[
                    html.Div(
                        id=ID_DB_STATUS,
                        className="flex items-center gap-2.5 px-3 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-xs",
                        children=[
                            html.Span(
                                className="relative flex h-2 w-2",
                                children=[
                                    html.Span(className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"),
                                    html.Span(className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400"),
                                ],
                            ),
                            html.Div([
                                html.Span("Supabase Cloud", className="block text-[11px] font-semibold text-slate-200 leading-tight"),
                                html.Span("174.7k trips loaded", className="block text-[10px] text-slate-400 leading-tight"),
                            ]),
                            html.Span(
                                "LIVE",
                                className="ml-auto text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
