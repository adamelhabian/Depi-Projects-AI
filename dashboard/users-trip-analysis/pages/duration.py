from dash import html, dcc

from components.kpi_card import create_kpi_card
from components.filter_dropdown import create_filter_dropdown

from charts.duration_charts import (
    create_user_duration_chart,
    create_hour_duration_chart
)


def create_duration_page(df):

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

    avg_duration = df["duration_min"].mean()

    fig_user_duration = create_user_duration_chart(df)
    fig_hour_duration = create_hour_duration_chart(df)

    return html.Div(

        children=[

            html.H2(
                "Average Duration",
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
                                "duration-gender-filter",
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
                                "duration-user-filter",
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
                "Average Trip Duration",
                f"{avg_duration:.2f} min",
                value_id="duration-kpi"
            ),

            html.Div(

                children=[

                    dcc.Graph(
                        id="duration-user-chart",
                        figure=fig_user_duration
                    ),

                    dcc.Graph(
                        id="duration-hour-chart",
                        figure=fig_hour_duration
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