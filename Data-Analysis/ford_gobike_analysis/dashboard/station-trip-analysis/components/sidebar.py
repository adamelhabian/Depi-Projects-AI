"""
components/sidebar.py – Sticky Navigation Sidebar & Mobile Drawer
==================================================================
Renders the analytical dashboard navigation sidebar with:

  - Desktop: sticky left column (w-64), always visible on lg+ screens
  - Mobile:  slide-in drawer with backdrop, toggled by hamburger button

Structure:
  FORD GOBIKE
  Analytics Dashboard
  ────────────────────────────
  📍 Station Analysis
     • Network Overview
     • Station Traffic
     • Flow Analysis
  ⏱ Time Analysis
     • Hourly Demand
     • Day × Hour
     • Duration Patterns
  👥 User Analysis
     • User Type
     • Demographics
     • User Type × Age
  🚚 Fleet Dispatch
     • Rebalancing Plan
  ────────────────────────────
  [Bay Wheels System · Live]

Design invariants:
  - The desktop sidebar and the mobile drawer are two SEPARATE DOM trees,
    each with its own unique set of Dash IDs. This avoids duplicate IDs in
    the browser DOM and lets clientside callbacks target each tree cleanly.
  - Both trees share the same visual design and navigation structure.
  - No server-side callbacks live here — all navigation behavior is handled
    clientside in Phase 3.
"""

from __future__ import annotations

from dash import html

from config import (
    # Shells
    ID_SIDEBAR_CONTAINER,
    ID_MOBILE_SIDEBAR,
    ID_MOBILE_BACKDROP,

    # Section keys
    SECTION_KEY_STATION,
    SECTION_KEY_TIME,
    SECTION_KEY_USER,
    SECTION_KEY_DISPATCH,

    # Desktop nav buttons
    ID_NAV_STATION_DESKTOP,
    ID_NAV_TIME_DESKTOP,
    ID_NAV_USER_DESKTOP,
    ID_NAV_DISPATCH_DESKTOP,

    # Desktop anchors
    ID_ANCHOR_STATION_NETWORK_DESKTOP,
    ID_ANCHOR_STATION_TRAFFIC_DESKTOP,
    ID_ANCHOR_STATION_FLOW_DESKTOP,
    ID_ANCHOR_TIME_HOURLY_DESKTOP,
    ID_ANCHOR_TIME_DAYHOUR_DESKTOP,
    ID_ANCHOR_TIME_DURATION_DESKTOP,
    ID_ANCHOR_USER_TYPE_DESKTOP,
    ID_ANCHOR_USER_DEMO_DESKTOP,
    ID_ANCHOR_USER_CROSSTAB_DESKTOP,
    ID_ANCHOR_DISPATCH_PLAN_DESKTOP,

    # Mobile nav buttons
    ID_NAV_STATION_MOBILE,
    ID_NAV_TIME_MOBILE,
    ID_NAV_USER_MOBILE,
    ID_NAV_DISPATCH_MOBILE,

    # Mobile anchors
    ID_ANCHOR_STATION_NETWORK_MOBILE,
    ID_ANCHOR_STATION_TRAFFIC_MOBILE,
    ID_ANCHOR_STATION_FLOW_MOBILE,
    ID_ANCHOR_TIME_HOURLY_MOBILE,
    ID_ANCHOR_TIME_DAYHOUR_MOBILE,
    ID_ANCHOR_TIME_DURATION_MOBILE,
    ID_ANCHOR_USER_TYPE_MOBILE,
    ID_ANCHOR_USER_DEMO_MOBILE,
    ID_ANCHOR_USER_CROSSTAB_MOBILE,
    ID_ANCHOR_DISPATCH_PLAN_MOBILE,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _nav_icon(text: str) -> html.Span:
    """Render an emoji-style icon in a fixed-width slot for alignment."""
    return html.Span(
        text,
        className="w-5 text-center text-base leading-none select-none",
        **{"aria-hidden": "true"},
    )


def _nav_button(
    nav_id: str,
    section_key: str,
    icon: str,
    label: str,
) -> html.Button:
    """
    Top-level section navigation button.

    `data-section` is read by the clientside callback to update
    ID_ACTIVE_SECTION_STORE. The `m5-nav-button` class serves as a styling
    hook for the active/inactive states.
    """
    return html.Button(
        [
            _nav_icon(icon),
            html.Span(
                label,
                className="font-semibold text-sm tracking-tight",
            ),
        ],
        id=nav_id,
        n_clicks=0,
        **{"data-section": section_key},
        className=(
            "m5-nav-button group w-full flex items-center gap-3 px-3 py-2.5 "
            "rounded-lg text-slate-600 hover:bg-slate-100 hover:text-slate-900 "
            "transition-colors duration-150 cursor-pointer text-left"
        ),
    )


def _sublink(anchor_id: str, label: str) -> html.Button:
    """
    Sub-link under a section. Rendered as a button (not a link) so we can
    drive clientside scroll behavior without touching the URL or adding
    dcc.Location. `data-anchor` is read by the clientside callback.
    """
    return html.Button(
        label,
        id=anchor_id,
        n_clicks=0,
        **{"data-anchor": anchor_id},
        className=(
            "m5-sublink block w-full text-left text-[13px] leading-tight "
            "pl-11 pr-2 py-1.5 rounded-md text-slate-500 "
            "hover:text-slate-900 hover:bg-slate-50 transition-colors "
            "duration-150 cursor-pointer"
        ),
    )


def _section_group(
    icon: str,
    label: str,
    nav_id: str,
    section_key: str,
    sublinks: list[tuple[str, str]],
) -> html.Div:
    """A top-level nav button followed by its sub-links."""
    return html.Div(
        className="mb-1",
        children=[
            _nav_button(nav_id, section_key, icon, label),
            html.Div(
                className="mt-0.5 space-y-0.5",
                children=[_sublink(aid, lbl) for aid, lbl in sublinks],
            ),
        ],
    )


def _sidebar_header() -> html.Div:
    """Compact brand header: Ford GoBike / Analytics Dashboard."""
    return html.Div(
        className="px-4 pt-5 pb-4 border-b border-slate-200",
        children=[
            html.Div(
                "Ford GoBike",
                className="text-base font-extrabold tracking-tight text-slate-900",
            ),
            html.Div(
                "Analytics Dashboard",
                className="text-[11px] font-medium uppercase tracking-wider text-slate-400 mt-0.5",
            ),
        ],
    )


def _sidebar_footer() -> html.Div:
    """Small footer status pill (visual continuity with the header pill)."""
    return html.Div(
        className="px-4 py-3 border-t border-slate-200 mt-auto",
        children=[
            html.Div(
                className="flex items-center gap-2 text-[11px] font-semibold text-slate-500",
                children=[
                    html.Span(
                        className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse inline-block",
                    ),
                    html.Span("Bay Wheels System · Live"),
                ],
            ),
        ],
    )


def _sidebar_content(
    nav_ids: dict,
    anchor_ids: dict,
) -> html.Div:
    """
    Build the shared sidebar content using the given set of Dash IDs.

    This function is called twice — once for the desktop tree and once for
    the mobile tree — each time with a DIFFERENT set of unique IDs, so the
    resulting DOM never contains duplicates.
    """
    return html.Div(
        className="flex flex-col h-full",
        children=[
            _sidebar_header(),

            html.Nav(
                className="flex-1 overflow-y-auto px-2 py-3",
                **{"aria-label": "Dashboard sections"},
                children=[
                    _section_group(
                        icon="📍",
                        label="Station Analysis",
                        nav_id=nav_ids["station"],
                        section_key=SECTION_KEY_STATION,
                        sublinks=[
                            (anchor_ids["station_network"], "Network Overview"),
                            (anchor_ids["station_traffic"], "Station Traffic"),
                            (anchor_ids["station_flow"],    "Flow Analysis"),
                        ],
                    ),
                    _section_group(
                        icon="⏱",
                        label="Time Analysis",
                        nav_id=nav_ids["time"],
                        section_key=SECTION_KEY_TIME,
                        sublinks=[
                            (anchor_ids["time_hourly"],   "Hourly Demand"),
                            (anchor_ids["time_dayhour"],  "Day × Hour"),
                            (anchor_ids["time_duration"], "Duration Patterns"),
                        ],
                    ),
                    _section_group(
                        icon="👥",
                        label="User Analysis",
                        nav_id=nav_ids["user"],
                        section_key=SECTION_KEY_USER,
                        sublinks=[
                            (anchor_ids["user_type"],     "User Type"),
                            (anchor_ids["user_demo"],     "Demographics"),
                            (anchor_ids["user_crosstab"], "User Type × Age"),
                        ],
                    ),
                    _section_group(
                        icon="🚚",
                        label="Fleet Dispatch",
                        nav_id=nav_ids["dispatch"],
                        section_key=SECTION_KEY_DISPATCH,
                        sublinks=[
                            (anchor_ids["dispatch_plan"], "Rebalancing Plan"),
                        ],
                    ),
                ],
            ),

            _sidebar_footer(),
        ],
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def sidebar() -> html.Aside:
    """
    Sticky desktop sidebar.

    Rendered as a fixed-width column (w-64) that sticks to the top of the
    viewport on lg+ screens. Hidden entirely on smaller screens (the mobile
    drawer below takes over).
    """
    desktop_nav_ids = {
        "station":  ID_NAV_STATION_DESKTOP,
        "time":     ID_NAV_TIME_DESKTOP,
        "user":     ID_NAV_USER_DESKTOP,
        "dispatch": ID_NAV_DISPATCH_DESKTOP,
    }
    desktop_anchor_ids = {
        "station_network": ID_ANCHOR_STATION_NETWORK_DESKTOP,
        "station_traffic": ID_ANCHOR_STATION_TRAFFIC_DESKTOP,
        "station_flow":    ID_ANCHOR_STATION_FLOW_DESKTOP,

        "time_hourly":     ID_ANCHOR_TIME_HOURLY_DESKTOP,
        "time_dayhour":    ID_ANCHOR_TIME_DAYHOUR_DESKTOP,
        "time_duration":   ID_ANCHOR_TIME_DURATION_DESKTOP,

        "user_type":       ID_ANCHOR_USER_TYPE_DESKTOP,
        "user_demo":       ID_ANCHOR_USER_DEMO_DESKTOP,
        "user_crosstab":   ID_ANCHOR_USER_CROSSTAB_DESKTOP,

        "dispatch_plan":   ID_ANCHOR_DISPATCH_PLAN_DESKTOP,
    }

    return html.Aside(
        id=ID_SIDEBAR_CONTAINER,
        className=(
            "hidden lg:flex lg:flex-col "
            "w-64 shrink-0 "
            "bg-white border-r border-slate-200 "
            "sticky top-0 h-screen "
            "z-30"
        ),
        **{"aria-label": "Primary navigation"},
        children=[_sidebar_content(desktop_nav_ids, desktop_anchor_ids)],
    )


def mobile_sidebar() -> list:
    """
    Mobile drawer + backdrop.

    Both elements are hidden by default (via inline `display:none`) and are
    toggled clientside in Phase 3 via ID_MOBILE_MENU_STORE.

    The mobile tree uses its OWN unique set of Dash IDs (the `*_MOBILE`
    variants from config.py), so there is no ID duplication with the
    desktop tree.
    """
    mobile_nav_ids = {
        "station":  ID_NAV_STATION_MOBILE,
        "time":     ID_NAV_TIME_MOBILE,
        "user":     ID_NAV_USER_MOBILE,
        "dispatch": ID_NAV_DISPATCH_MOBILE,
    }
    mobile_anchor_ids = {
        "station_network": ID_ANCHOR_STATION_NETWORK_MOBILE,
        "station_traffic": ID_ANCHOR_STATION_TRAFFIC_MOBILE,
        "station_flow":    ID_ANCHOR_STATION_FLOW_MOBILE,

        "time_hourly":     ID_ANCHOR_TIME_HOURLY_MOBILE,
        "time_dayhour":    ID_ANCHOR_TIME_DAYHOUR_MOBILE,
        "time_duration":   ID_ANCHOR_TIME_DURATION_MOBILE,

        "user_type":       ID_ANCHOR_USER_TYPE_MOBILE,
        "user_demo":       ID_ANCHOR_USER_DEMO_MOBILE,
        "user_crosstab":   ID_ANCHOR_USER_CROSSTAB_MOBILE,

        "dispatch_plan":   ID_ANCHOR_DISPATCH_PLAN_MOBILE,
    }

    backdrop = html.Div(
        id=ID_MOBILE_BACKDROP,
        style={"display": "none"},
        className=(
            "fixed inset-0 bg-slate-900/40 backdrop-blur-[2px] z-40 "
            "lg:hidden"
        ),
        **{"aria-hidden": "true"},
    )

    drawer = html.Aside(
        id=ID_MOBILE_SIDEBAR,
        style={"display": "none"},
        className=(
            "fixed top-0 left-0 h-full w-64 bg-white border-r border-slate-200 "
            "shadow-2xl z-50 lg:hidden"
        ),
        **{"aria-label": "Mobile navigation"},
        children=[_sidebar_content(mobile_nav_ids, mobile_anchor_ids)],
    )

    return [backdrop, drawer]