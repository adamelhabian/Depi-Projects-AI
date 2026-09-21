"""
pages/time_user_page.py – Time & User Demographics Analysis View
================================================================
Integrates Member 4 (Time & User Behavior Analysis) into the Master Dashboard shell.
"""

from __future__ import annotations

from dash import html
from utils.module_loader import get_time_user_module


def render_time_user_page() -> html.Div:
    """
    Renders the Time & User Behavior Analysis layout seamlessly within the master dashboard.
    """
    create_layout_fn, _ = get_time_user_module()
    return html.Div(
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6",
        children=[
            create_layout_fn(),
        ],
    )
