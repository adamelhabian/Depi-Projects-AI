"""
pages/station_page.py – Station & Network Flow Analysis View
============================================================
Integrates Member 5 (Station & Trip Analysis) into the Master Dashboard shell.
"""

from __future__ import annotations

from dash import html
from utils.module_loader import get_station_module


def render_station_page() -> html.Div:
    """
    Renders the Station & Trip Analysis layout seamlessly within the master dashboard.
    """
    create_layout_fn, _ = get_station_module()
    return html.Div(
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6",
        children=[
            create_layout_fn(),
        ],
    )
