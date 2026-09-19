"""
app.py – Ford GoBike Master Dashboard Application Entry Point
==============================================================
Central Enterprise BI application uniting:
  - Executive Overview
  - Member 5: Station & Network Flow Analysis
  - Member 4: Time & User Demographics Analysis

Run Standalone:
    python app.py
    (Opens http://127.0.0.1:8050)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure master-dashboard root is on sys.path
_CURRENT_DIR = Path(__file__).resolve().parent
if str(_CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(_CURRENT_DIR))

from dash import Dash
from config import APP_TITLE, APP_HOST, APP_PORT, DEBUG_MODE
from layout import create_master_layout
from callbacks.routing import register_routing_callbacks
from callbacks.global_filter_callbacks import register_global_filter_callbacks
from callbacks.global_filter_sync import register_global_filter_sync_callbacks
from utils.module_loader import get_station_module, get_time_user_module

# ---------------------------------------------------------------------------
# 1. Application Initialization
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    title=APP_TITLE,
    assets_folder=str(_CURRENT_DIR / "assets"),
    external_scripts=[
        "https://cdn.tailwindcss.com",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js",
    ],
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    ],
    suppress_callback_exceptions=True,
)

# Custom HTML Index Shell
app.index_string = """<!DOCTYPE html>
<html lang="en">
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {%css%}
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                    },
                    colors: {
                        brand: {
                            50: '#f0fdf4',
                            500: '#10b981',
                            600: '#059669',
                            700: '#047857',
                        }
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-slate-50 text-slate-900 font-sans antialiased selection:bg-indigo-500 selection:text-white">
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
"""

# Expose WSGI server for production deployment (Gunicorn / uWSGI)
server = app.server

# ---------------------------------------------------------------------------
# 2. Layout Definition
# ---------------------------------------------------------------------------
app.layout = create_master_layout()

# ---------------------------------------------------------------------------
# 3. Callbacks Registration
# ---------------------------------------------------------------------------
print(">> Initializing Master Dashboard Routing Callbacks...", flush=True)
register_routing_callbacks(app)

print(">> Registering Global Filter Bar Callbacks...", flush=True)
register_global_filter_callbacks(app)

print(">> Registering Member 5 (Station Analysis) Callbacks...", flush=True)
_, register_station_callbacks = get_station_module()
register_station_callbacks(app)

print(">> Registering Member 4 (Time & User Analysis) Callbacks...", flush=True)
_, register_time_user_callbacks = get_time_user_module()
register_time_user_callbacks(app)

print(">> Registering Global->Local Filter Bridge Callbacks...", flush=True)
register_global_filter_sync_callbacks(app)

print(f">> Total Callbacks Registered: {len(app.callback_map)}", flush=True)

# ---------------------------------------------------------------------------
# 4. Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"\n=======================================================")
    print(f"   Ford GoBike Master Analytics Platform Running")
    print(f"   URL: http://{APP_HOST}:{APP_PORT}")
    print(f"=======================================================\n")
    app.run(
        debug=DEBUG_MODE,
        host=APP_HOST,
        port=APP_PORT,
    )
