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
    external_scripts=[
        "https://cdn.tailwindcss.com",
    ],
    suppress_callback_exceptions=True,
)

# Custom HTML index matching station_trip_analysis.html
app.index_string = """<!DOCTYPE html>
<html lang="en">
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    {%css%}
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
        }
    </style>
</head>
<body class="p-4 sm:p-6 lg:p-8 max-w-[1600px] mx-auto min-h-screen flex flex-col">
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>"""

# Attach layout and callbacks
app.layout = create_layout()
register_callbacks(app)

# Expose WSGI server instance for production deployment
server = app.server

if __name__ == "__main__":
    is_debug = os.environ.get("DASH_DEBUG", "True").lower() in {"true", "1", "yes"}
    port = int(os.environ.get("PORT", 8050))

    # Pre-warm cached dataset so data is verified and loaded from Supabase immediately on startup
    if not is_debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print(">> [STARTUP] Pre-loading dataset from Supabase...", flush=True)
        from data_loader import load_clean_data
        load_clean_data()

    app.run(debug=is_debug, port=port)

