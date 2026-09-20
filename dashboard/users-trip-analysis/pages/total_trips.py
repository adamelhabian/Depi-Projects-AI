from dash import html, dcc

from components.kpi_card import create_kpi_card
from components.filter_dropdown import create_filter_dropdown

from charts.trip_charts import (
    # create_monthly_trips_chart,
    create_daily_trips_chart
)


def create_total_trips_page(df):

    user_types = sorted(
        df["user_type"]
        .dropna()
        .unique()
    )

    genders = sorted(
        df["member_gender"]
        .dropna()
        .unique()
    )

    total_trips = df["trip_id"].nunique()

    fig_daily = create_daily_trips_chart(df)

    return html.Div(

        children=[

            html.H2(
                "Total Trips",
                style={
                    "marginBottom": "20px"
                }
            ),

            # Filters
            html.Div(

                children=[

                    html.Div(
                        children=[

                            html.P(
                                "Gender",
                                style={
                                    "fontWeight": "bold",
                                    "marginBottom": "8px"
                                }
                            ),

                            create_filter_dropdown(
                                "total-gender-filter",
                                "Gender",
                                genders
                            )
                        ]
                    ),

                    html.Div(
                        children=[

                            html.P(
                                "User Type",
                                style={
                                    "fontWeight": "bold",
                                    "marginBottom": "8px"
                                }
                            ),

                            create_filter_dropdown(
                                "total-user-filter",
                                "User Type",
                                user_types
                            )
                        ]
                    )

                ],

                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "20px",

                    "backgroundColor": "white",

                    "padding": "20px",

                    "borderRadius": "12px",

                    "marginBottom": "25px"
                }
            ),

            # KPI
            create_kpi_card(
                "Total Trips",
                f"{total_trips:,}",
                value_id="total-trips-kpi"
            ),

            # Charts
            html.Div(

                children=[


                    dcc.Graph(
                        id="total-daily-chart",
                        figure=fig_daily
                    )

                ],

                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr",
                    "gap": "20px"
                }
            )

        ],

        style={
            "padding": "30px"
        }
    )