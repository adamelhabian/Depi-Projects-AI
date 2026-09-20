from dash import html, dcc

from components.kpi_card import create_kpi_card
from components.filter_dropdown import create_filter_dropdown

from charts.user_charts import (
    create_user_type_chart,
    create_gender_user_chart
)


def create_users_page(df):


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

    subscriber_trips = (
        df.loc[
            df["user_type"] == "Subscriber",
            "trip_id"
        ]
        .nunique()
    )

    fig_user_type = create_user_type_chart(df)
    fig_gender = create_gender_user_chart(df)

    return html.Div(

        children=[

            html.H2(
                "User Analysis",
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
                                "User Type",
                                style={
                                    "fontWeight": "bold",
                                    "marginBottom": "8px"
                                }
                            ),

                            create_filter_dropdown(
                                "users-user-filter",
                                "User Type",
                                user_types
                            )
                        ]
                    ),

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
                                "users-gender-filter",
                                "Gender",
                                genders
                            )
                        ]
                    )

                ],

                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr 1fr",
                    "gap": "20px",

                    "backgroundColor": "white",

                    "padding": "20px",

                    "borderRadius": "12px",

                    "marginBottom": "25px"
                }
            ),

            create_kpi_card(
                "Subscriber Trips",
                f"{subscriber_trips:,}",
                value_id="subscriber-trips-kpi"
            ),

            html.Div(

                children=[

                    dcc.Graph(
                        id="users-type-chart",
                        figure=fig_user_type
                    ),

                    dcc.Graph(
                        id="users-gender-chart",
                        figure=fig_gender
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