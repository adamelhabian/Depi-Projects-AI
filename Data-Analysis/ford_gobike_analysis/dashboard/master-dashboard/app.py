"""
app.py – Ford GoBike Master Modern Analytics Platform
=====================================================
Unified enterprise SaaS analytics application:
  - Dash Engine with multi-page URL routing: "/", "/stations", "/time-user"
  - Tailwind CSS via Play CDN + Inter typography + design tokens
  - Interactive Plotly figures bound to real Supabase Gold layer data
  - Seamless responsive layout with fixed sidebar and sticky filter bar

Run Standalone:
    python app.py
    (Serves at http://127.0.0.1:8050)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure master-dashboard root is on sys.path
_CURRENT_DIR = Path(__file__).resolve().parent
if str(_CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(_CURRENT_DIR))

from dash import Dash
from flask import jsonify, send_from_directory
from config import APP_TITLE, APP_HOST, APP_PORT, DEBUG_MODE
from layout import create_master_layout
from callbacks.routing import register_routing_callbacks
from callbacks.global_filter_callbacks import register_global_filter_callbacks
from callbacks.station_callbacks import register_station_callbacks
from data_loader import get_full_api_payload

# ---------------------------------------------------------------------------
# 1. Application Initialization & SaaS Index Shell
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    title=APP_TITLE,
    routes_pathname_prefix="/",
    assets_folder=str(_CURRENT_DIR / "assets"),
    suppress_callback_exceptions=True,
)

# Enterprise SaaS HTML5 Shell with Tailwind Play CDN & Inter Typography
app.index_string = """<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                        sans: ['Inter', -apple-system, 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
                    },
                    colors: {
                        brand: {
                            dark: '#0B1329',
                            DEFAULT: '#14B8A6',
                        },
                        subscriber: {
                            DEFAULT: '#14B8A6',
                            dark: '#0F766E',
                            soft: 'rgba(20, 184, 166, 0.12)',
                        },
                        customer: {
                            DEFAULT: '#A855F7',
                            dark: '#7E22CE',
                            soft: 'rgba(168, 85, 247, 0.12)',
                        },
                        deficit: {
                            DEFAULT: '#F97316',
                            dark: '#C2410C',
                            soft: 'rgba(249, 115, 22, 0.14)',
                        },
                        surplus: {
                            DEFAULT: '#3B82F6',
                            dark: '#1D4ED8',
                            soft: 'rgba(59, 130, 246, 0.14)',
                        },
                        balanced: '#94A3B8',
                    },
                    boxShadow: {
                        'card': '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
                        'card-hover': '0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.04)',
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #F8FAFC;
        }
        /* Custom scrollbars */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #F1F5F9;
        }
        ::-webkit-scrollbar-thumb {
            background: #CBD5E1;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94A3B8;
        }
    </style>
</head>
<body class="bg-slate-50 text-slate-900 font-sans antialiased selection:bg-teal-500 selection:text-white min-h-screen flex flex-col">
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
"""

# Expose WSGI server
server = app.server

# ---------------------------------------------------------------------------
# 2. Supplementary Endpoints
# ---------------------------------------------------------------------------
@server.route("/api/data")
def serve_api_data():
    """Provides real-time Supabase Gold data payload to developers or external tools."""
    return jsonify(get_full_api_payload())


@server.route("/interactive")
def serve_interactive():
    """Optional reference HTML5 view."""
    return send_from_directory(str(_CURRENT_DIR), "index.html")

# ---------------------------------------------------------------------------
# 3. Layout Mount
# ---------------------------------------------------------------------------
app.layout = create_master_layout()

# ---------------------------------------------------------------------------
# 4. Callbacks Registration
# ---------------------------------------------------------------------------
print(">> Registering URL Routing Callbacks...", flush=True)
register_routing_callbacks(app)

print(">> Registering Global Filter Bar Callbacks...", flush=True)
register_global_filter_callbacks(app)

print(">> Registering Station & Network Flow Callbacks...", flush=True)
register_station_callbacks(app)

print(f">> Master Dashboard Initialized! Total Callbacks: {len(app.callback_map)}", flush=True)

# ---------------------------------------------------------------------------
# 5. Local Entry Point
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
