import sys
from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


# =========================================================
# DASH
# =========================================================

from dash import Dash, html


# =========================================================
# DATABASE
# =========================================================

from dashboard.database import (
    load_dashboard_data
)


# =========================================================
# PAGES
# =========================================================

from pages.total_trips import (
    create_total_trips_page
)

from pages.duration import (
    create_duration_page
)

from pages.users import (
    create_users_page
)

from pages.stations import (
    create_stations_page
)


# =========================================================
# CALLBACKS
# =========================================================

from callbacks.dashboard_callbacks import (
    register_dashboard_callbacks
)


# =========================================================
# LOAD DATA
# =========================================================

df = load_dashboard_data()


# =========================================================
# CREATE APP
# =========================================================

app = Dash(
    __name__
)


# =========================================================
# LAYOUT
# =========================================================

app.layout = html.Div(

    children=[

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        html.Div(

            children=[

                html.H1(
                    "Ford GoBike Analysis Dashboard",

                    style={
                        "margin": "0",
                        "fontSize": "32px"
                    }
                ),

                html.P(
                    "Bike sharing trips analysis",

                    style={
                        "marginTop": "8px",
                        "marginBottom": "0"
                    }
                )

            ],

            style={
                "backgroundColor": "white",

                "padding": "25px 30px",

                "boxShadow":
                    "0 2px 8px rgba(0,0,0,0.08)"
            }
        ),


        # -------------------------------------------------
        # PAGES
        # -------------------------------------------------

        create_total_trips_page(df),

        create_duration_page(df),

        create_users_page(df),

        create_stations_page(df)

    ],

    style={
        "backgroundColor": "#f5f7fa",
        "minHeight": "100vh"
    }
)


# =========================================================
# REGISTER CALLBACKS
# =========================================================

register_dashboard_callbacks(
    app,
    df
)


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )