"""
components/station_inspector.py – Interactive Station Deep Dive Side Drawer
===========================================================================
Renders the slide-in side drawer panel over the map when a station is clicked:
  1. Header: station name, region badge, and traffic rank in region + close button.
  2. Two KPI tiles: Total Trips (with % share of network) & Net Imbalance (with status).
  3. Inbound vs Outbound split bar: stacked horizontal bar with raw counts below.
  4. Top 3 Connected Destinations list with volume badges.
  5. Round-trip ratio (%) with explanatory subtitle & smart rebalancing suggestion.
  6. Footer button: "Focus Map on Station" to re-center/zoom the map.
"""

from __future__ import annotations

from dash import html
from config import ID_DRAWER_CLOSE_BTN, ID_DRAWER_FOCUS_BTN


def render_station_inspector(profile: dict | None = None) -> html.Div:
    """
    Render the Station Deep Dive Side Drawer component.

    Parameters
    ----------
    profile : dict, optional
        Dictionary produced by compute_station_deep_dive().
        If None or station_name is empty/None Selected, renders a hidden/empty shell.

    Returns
    -------
    html.Div
    """
    if not profile or not profile.get("station_name") or profile.get("station_name") == "None Selected":
        # Return hidden shell containing dormant button IDs for callback registration safety
        return html.Div(
            className="drawer-inner-empty",
            children=[
                html.Button("✕", id=ID_DRAWER_CLOSE_BTN, style={"display": "none"}, n_clicks=0),
                html.Button("Focus Map", id=ID_DRAWER_FOCUS_BTN, style={"display": "none"}, n_clicks=0),
            ],
        )

    st_name = profile.get("station_name", "Unknown Station")
    region_code = profile.get("region_code", "SF")
    rank = profile.get("rank", 1)
    total = profile.get("total_traffic", 0)
    share_pct = profile.get("network_share_pct", 0.0)
    deps = profile.get("departures", 0)
    arrs = profile.get("arrivals", 0)
    net = profile.get("net_flow", 0)
    status_label = profile.get("status_label", "Balanced")
    inbound_pct = profile.get("inbound_pct", 50.0)
    outbound_pct = profile.get("outbound_pct", 50.0)
    top_dests = profile.get("top_destinations", [])
    rt_pct = profile.get("round_trip_pct", 0.0)
    recommendation = profile.get("recommendation", "Self-balancing corridor hub.")

    flow_color = "#059669" if net >= 0 else "#DC2626"

    return html.Div(
        className="station-drawer-content",
        children=[
            # ── 1. Drawer Header ─────────────────────────────────────────
            html.Div(
                className="drawer-header",
                children=[
                    html.Div(
                        style={"flex": "1", "minWidth": "0"},
                        children=[
                            html.Div(
                                style={"display": "flex", "alignItems": "center", "gap": "6px", "marginBottom": "4px"},
                                children=[
                                    html.Span(region_code, className="drawer-badge-region"),
                                    html.Span(f"Rank #{rank} in Region", className="drawer-badge-rank"),
                                ],
                            ),
                            html.H3(st_name, className="drawer-station-name", title=st_name),
                        ],
                    ),
                    html.Button(
                        "✕",
                        id=ID_DRAWER_CLOSE_BTN,
                        className="drawer-close-btn",
                        n_clicks=0,
                        title="Close Drawer",
                    ),
                ],
            ),

            # ── 2. Drawer Body ───────────────────────────────────────────
            html.Div(
                className="drawer-body",
                children=[
                    # ── Two KPI Summary Tiles Side by Side ───────────────
                    html.Div(
                        className="drawer-tile-grid",
                        children=[
                            # Tile 1: Total Trips & % share
                            html.Div(
                                className="drawer-kpi-tile",
                                children=[
                                    html.Span("TOTAL TRIPS", className="drawer-kpi-label"),
                                    html.Span(f"{total:,}", className="drawer-kpi-val"),
                                    html.Span(f"{share_pct:.1f}% of filtered network", className="drawer-kpi-sub"),
                                ],
                            ),
                            # Tile 2: Net Imbalance & Surplus/Deficit label
                            html.Div(
                                className="drawer-kpi-tile",
                                children=[
                                    html.Span("NET IMBALANCE", className="drawer-kpi-label"),
                                    html.Span(
                                        f"{net:+,}",
                                        className="drawer-kpi-val",
                                        style={"color": flow_color},
                                    ),
                                    html.Span(
                                        status_label,
                                        className="drawer-kpi-sub",
                                        style={"color": flow_color, "fontWeight": "600"},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # ── 3. Inbound vs Outbound Split Bar ─────────────────
                    html.Div(
                        className="drawer-split-box",
                        children=[
                            html.Div(
                                className="drawer-split-header",
                                children=[
                                    html.Span("Trip Flow Split", style={"fontWeight": "600"}),
                                    html.Span(f"{inbound_pct:.0f}% In / {outbound_pct:.0f}% Out", style={"color": "#64748B"}),
                                ],
                            ),
                            html.Div(
                                className="drawer-split-track",
                                children=[
                                    html.Div(
                                        className="drawer-split-inbound",
                                        style={"width": f"{inbound_pct}%"},
                                        title=f"Inbound: {arrs:,} ({inbound_pct:.1f}%)",
                                    ),
                                    html.Div(
                                        className="drawer-split-outbound",
                                        style={"width": f"{outbound_pct}%"},
                                        title=f"Outbound: {deps:,} ({outbound_pct:.1f}%)",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="drawer-split-labels",
                                children=[
                                    html.Span([
                                        html.Span("● ", style={"color": "#10B981"}),
                                        "Inbound: ",
                                        html.Strong(f"{arrs:,}"),
                                    ]),
                                    html.Span([
                                        html.Span("● ", style={"color": "#F43F5E"}),
                                        "Outbound: ",
                                        html.Strong(f"{deps:,}"),
                                    ]),
                                ],
                            ),
                        ],
                    ),

                    # ── 4. Top 3 Connected Destinations ──────────────────
                    html.Div(
                        className="drawer-dest-box",
                        children=[
                            html.Div("Top 3 Connected Destinations", className="drawer-dest-title"),
                            html.Div(
                                className="drawer-dest-list",
                                children=[
                                    html.Div(
                                        className="drawer-dest-item",
                                        children=[
                                            html.Span(
                                                f"{idx + 1}. {item['station'].split('(')[0].strip()}",
                                                className="drawer-dest-name",
                                                title=item["station"],
                                            ),
                                            html.Span(f"{item['count']:,} trips", className="drawer-dest-badge"),
                                        ],
                                    )
                                    for idx, item in enumerate(top_dests[:3])
                                ] if top_dests else [
                                    html.Div("No outbound journeys recorded.", style={"color": "#94A3B8", "fontStyle": "italic", "fontSize": "11px"})
                                ],
                            ),
                        ],
                    ),

                    # ── 5. Round-Trip Ratio & Rebalancing Suggestion ──────
                    html.Div(
                        className="drawer-rt-box",
                        children=[
                            html.Div(
                                className="drawer-rt-header",
                                children=[
                                    html.Div([
                                        html.Span("Round-Trip Ratio", style={"fontWeight": "700", "fontSize": "12px", "color": "#0F172A", "display": "block"}),
                                        html.Span("trips starting and ending here", style={"fontSize": "10px", "color": "#94A3B8"}),
                                    ]),
                                    html.Span(f"{rt_pct:.1f}%", style={"fontSize": "16px", "fontWeight": "800", "color": "#0F172A"}),
                                ],
                            ),
                            html.Div(
                                className="drawer-rec-box",
                                children=[
                                    html.Strong("Rebalance Suggestion: ", style={"color": "#334155"}),
                                    recommendation,
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # ── 6. Footer Button: Focus Map on Station ───────────────────
            html.Div(
                className="drawer-footer",
                children=[
                    html.Button(
                        [
                            html.Span("🎯", style={"marginRight": "6px"}),
                            "Focus Map on Station",
                        ],
                        id=ID_DRAWER_FOCUS_BTN,
                        className="drawer-focus-btn",
                        n_clicks=0,
                    ),
                ],
            ),
        ],
    )
