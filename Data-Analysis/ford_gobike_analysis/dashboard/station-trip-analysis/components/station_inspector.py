"""
components/station_inspector.py – Interactive Station Profile Inspector
========================================================================
Renders deep-dive profile for a station when clicked on the map or ranking chart:
  - Header: Station name, Metro Region badge, total trips count.
  - KPI Stat Badges: Departures, Arrivals, Net Flow, Imbalance Ratio %, Round-Trip %.
  - Drill-down lists: Top 5 Destinations and Top 5 Origins.
"""

from __future__ import annotations

from dash import html
from config import COLORS


def render_station_inspector(profile: dict | None = None) -> html.Div:
    """
    Render the Station Profile Inspector container.

    Parameters
    ----------
    profile : dict, optional
        Dictionary produced by compute_station_deep_dive().
        If None or station_name is empty/None Selected, displays empty prompt.

    Returns
    -------
    html.Div
    """
    if not profile or not profile.get("station_name") or profile.get("station_name") == "None Selected":
        return html.Div(
            className="dashboard-card inspector-card inspector-empty",
            children=[
                html.Div(
                    className="inspector-placeholder",
                    children=[
                        html.Span("📍", className="inspector-placeholder-icon"),
                        html.H4("Station Profile Inspector", className="inspector-placeholder-title"),
                        html.P(
                            "Click any station node on the map or bar on the Top Stations chart "
                            "to inspect its detailed inbound/outbound breakdown, turnover ratio, "
                            "and top connected destinations & origins.",
                            className="inspector-placeholder-text",
                        ),
                    ],
                )
            ],
        )

    st_name = profile["station_name"]
    region = profile.get("region", "Unknown")
    total = profile.get("total_traffic", 0)
    deps = profile.get("departures", 0)
    arrs = profile.get("arrivals", 0)
    net = profile.get("net_flow", 0)
    imb_ratio = profile.get("imbalance_ratio", 0.0)
    rt_count = profile.get("round_trip_count", 0)
    rt_pct = profile.get("round_trip_pct", 0.0)
    top_dests = profile.get("top_destinations", [])
    top_origs = profile.get("top_origins", [])

    # Flow badge styling
    flow_color = COLORS["success"] if net >= 0 else COLORS["danger"]
    flow_label = "Inbound Pressure (Surplus)" if net >= 0 else "Outbound Pressure (Deficit)"

    return html.Div(
        className="dashboard-card inspector-card",
        children=[
            # ── Header ──────────────────────────────────────────
            html.Div(
                className="inspector-header",
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "4px"},
                                children=[
                                    html.Span("STATION INSPECTOR", className="badge-tag"),
                                    html.Span(region, className="badge-region"),
                                ],
                            ),
                            html.H3(st_name, className="inspector-title"),
                        ]
                    ),
                    html.Div(
                        className="inspector-total-badge",
                        children=[
                            html.Span(f"{total:,}", className="inspector-total-val"),
                            html.Span("Total Trips", className="inspector-total-label"),
                        ],
                    ),
                ],
            ),

            # ── KPI Stat Row ────────────────────────────────────
            html.Div(
                className="inspector-kpi-grid",
                children=[
                    html.Div(
                        className="inspector-kpi-item",
                        children=[
                            html.Span("Departures", className="inspector-kpi-label"),
                            html.Span(f"{deps:,}", className="inspector-kpi-val"),
                            html.Span("Outbound Trips", className="inspector-kpi-sub"),
                        ],
                    ),
                    html.Div(
                        className="inspector-kpi-item",
                        children=[
                            html.Span("Arrivals", className="inspector-kpi-label"),
                            html.Span(f"{arrs:,}", className="inspector-kpi-val"),
                            html.Span("Inbound Trips", className="inspector-kpi-sub"),
                        ],
                    ),
                    html.Div(
                        className="inspector-kpi-item",
                        children=[
                            html.Span("Net Flow", className="inspector-kpi-label"),
                            html.Span(
                                f"{net:+,} ({imb_ratio:+.1f}%)",
                                className="inspector-kpi-val",
                                style={"color": flow_color},
                            ),
                            html.Span(flow_label, className="inspector-kpi-sub", style={"color": flow_color}),
                        ],
                    ),
                    html.Div(
                        className="inspector-kpi-item",
                        children=[
                            html.Span("Round-Trip Leisure", className="inspector-kpi-label"),
                            html.Span(f"{rt_pct:.1f}%", className="inspector-kpi-val", style={"color": "#F59E0B"}),
                            html.Span(f"{rt_count:,} Same-Stn Trips", className="inspector-kpi-sub"),
                        ],
                    ),
                ],
            ),

            # ── Drill-Down Columns ───────────────────────────────
            html.Div(
                className="inspector-drilldown-grid",
                children=[
                    # Top Destinations
                    html.Div(
                        className="drilldown-col",
                        children=[
                            html.H4("Top Destinations (Outbound)", className="drilldown-col-title"),
                            html.Ul(
                                className="drilldown-list",
                                children=[
                                    html.Li(
                                        className="drilldown-item",
                                        children=[
                                            html.Span(f"{idx+1}. {item['station']}", className="drilldown-station"),
                                            html.Span(f"{item['count']:,} trips", className="drilldown-count"),
                                        ],
                                    )
                                    for idx, item in enumerate(top_dests)
                                ] if top_dests else [
                                    html.Li("No outbound trips recorded.", className="drilldown-empty")
                                ],
                            ),
                        ],
                    ),

                    # Top Origins
                    html.Div(
                        className="drilldown-col",
                        children=[
                            html.H4("Top Origins (Inbound)", className="drilldown-col-title"),
                            html.Ul(
                                className="drilldown-list",
                                children=[
                                    html.Li(
                                        className="drilldown-item",
                                        children=[
                                            html.Span(f"{idx+1}. {item['station']}", className="drilldown-station"),
                                            html.Span(f"{item['count']:,} trips", className="drilldown-count"),
                                        ],
                                    )
                                    for idx, item in enumerate(top_origs)
                                ] if top_origs else [
                                    html.Li("No inbound trips recorded.", className="drilldown-empty")
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
