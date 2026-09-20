from dash import html, dcc

from components.kpi_card import create_kpi_card
from components.filter_dropdown import create_filter_dropdown

from charts.station_charts import (
    create_start_station_chart,
    create_end_station_chart
)


def create_stations_page(df):

    genders = sorted(
        df["member_gender"]
        .dropna()
        .unique()
    )

    user_types = sorted(
        df["user_type"]
        .dropna()
        .unique()
    )

    station_counts = (
        df.dropna(
            subset=["start_station_name"]
        )
        .groupby("start_station_name")["trip_id"]
        .nunique()
        .sort_values(ascending=False)
    )

    if not station_counts.empty:
        popular_station = station_counts.index[0]
    else:
        popular_station = "N/A"

    fig_start = create_start_station_chart(df)
    fig_end = create_end_station_chart(df)

    return html.Div(

        children=[

            html.H2(
                "Station Analysis",
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
                                "stations-gender-filter",
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
                                "stations-user-filter",
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

            create_kpi_card(
                "Most Popular Start Station",
                popular_station,
                value_id="popular-station-kpi"
            ),

            html.Div(

                children=[

                    dcc.Graph(
                        id="stations-start-chart",
                        figure=fig_start
                    ),

                    dcc.Graph(
                        id="stations-end-chart",
                        figure=fig_end
                    )

                ],

                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "20px"
                }
            )

        ],

        style={
            "padding": "30px"
        }
    )