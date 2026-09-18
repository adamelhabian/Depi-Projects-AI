"""
app.py – Member 5: Station & Trip Analysis Module Entry Point
=============================================================
Collaborative Ford GoBike Analytics Project · Member 5 Section

Run Standalone:
    python app.py
    (Opens http://127.0.0.1:8050)

Integration Contract for Team Dashboard (Members 3 & 4):
    from member5.layout import create_layout
    from member5.callbacks.dashboard_callbacks import register_callbacks

    # In your parent team layout:
    parent_layout.children.append(create_layout())

    # In your application setup:
    register_callbacks(team_app)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the module root is on sys.path regardless of execution working directory
_MODULE_DIR = Path(__file__).resolve().parent
if str(_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_MODULE_DIR))

from dash import Dash
from layout import create_layout
from callbacks.dashboard_callbacks import register_callbacks

# ---------------------------------------------------------------------------
# Application Initialization
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    title="Ford GoBike | Station & Trip Analysis (Member 5)",
    assets_folder=str(_MODULE_DIR / "assets"),
)

# Attach layout and callbacks
app.layout = create_layout()
register_callbacks(app)

# Expose WSGI server instance for production deployment
server = app.server

if __name__ == "__main__":
    # Configurable debug mode for local development vs production
    is_debug = os.environ.get("DASH_DEBUG", "True").lower() in {"true", "1", "yes"}
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=is_debug, port=port)

