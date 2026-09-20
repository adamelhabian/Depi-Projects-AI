from dash import Input, Output

from charts.trip_charts import (
    create_daily_trips_chart
)

from charts.duration_charts import (
    create_user_duration_chart,
    create_hour_duration_chart
)

from charts.user_charts import (
    create_user_type_chart,
    create_gender_user_chart
)

from charts.station_charts import (
    create_start_station_chart,
    create_end_station_chart
)


# =========================================================
# COMMON FILTER
# =========================================================

def filter_dataframe(
    df,
    selected_gender,
    selected_user
):

    filtered_df = df.copy()

    if selected_gender is not None:
        filtered_df = filtered_df[
            filtered_df["member_gender"] == selected_gender
        ]

    if selected_user is not None:
        filtered_df = filtered_df[
            filtered_df["user_type"] == selected_user
        ]

    return filtered_df


def register_dashboard_callbacks(app, df):

    # =====================================================
    # TOTAL TRIPS
    # =====================================================

    @app.callback(
        Output(
            "total-trips-kpi",
            "children"
        ),

        Output(
            "total-daily-chart",
            "figure"
        ),

        Input(
            "total-gender-filter",
            "value"
        ),

        Input(
            "total-user-filter",
            "value"
        )
    )
    def update_total_trips(
        selected_gender,
        selected_user
    ):

        filtered_df = filter_dataframe(
            df,
            selected_gender,
            selected_user
        )

        total_trips = filtered_df[
            "trip_id"
        ].nunique()

        daily_fig = create_daily_trips_chart(
            filtered_df
        )

        return (
            f"{total_trips:,}",
            daily_fig
        )


    # =====================================================
    # DURATION
    # =====================================================

    @app.callback(
        Output(
            "duration-kpi",
            "children"
        ),

        Output(
            "duration-user-chart",
            "figure"
        ),

        Output(
            "duration-hour-chart",
            "figure"
        ),

        Input(
            "duration-gender-filter",
            "value"
        ),

        Input(
            "duration-user-filter",
            "value"
        )
    )
    def update_duration(
        selected_gender,
        selected_user
    ):

        filtered_df = filter_dataframe(
            df,
            selected_gender,
            selected_user
        )

        if filtered_df.empty:

            return (
                "0.00 min",

                create_user_duration_chart(
                    filtered_df
                ),

                create_hour_duration_chart(
                    filtered_df
                )
            )

        avg_duration = filtered_df[
            "duration_min"
        ].mean()

        user_duration_fig = (
            create_user_duration_chart(
                filtered_df
            )
        )

        hour_duration_fig = (
            create_hour_duration_chart(
                filtered_df
            )
        )

        return (
            f"{avg_duration:.2f} min",
            user_duration_fig,
            hour_duration_fig
        )


    # =====================================================
    # USERS
    # =====================================================

    @app.callback(
        Output(
            "subscriber-trips-kpi",
            "children"
        ),

        Output(
            "users-type-chart",
            "figure"
        ),

        Output(
            "users-gender-chart",
            "figure"
        ),

        Input(
            "users-gender-filter",
            "value"
        ),

        Input(
            "users-user-filter",
            "value"
        )
    )
    def update_users(
        selected_gender,
        selected_user
    ):

        filtered_df = filter_dataframe(
            df,
            selected_gender,
            selected_user
        )

        subscriber_trips = (
            filtered_df.loc[
                filtered_df["user_type"] == "Subscriber",
                "trip_id"
            ]
            .nunique()
        )

        user_type_fig = create_user_type_chart(
            filtered_df
        )

        gender_fig = create_gender_user_chart(
            filtered_df
        )

        return (
            f"{subscriber_trips:,}",
            user_type_fig,
            gender_fig
        )


    # =====================================================
    # STATIONS
    # =====================================================

    @app.callback(
        Output(
            "popular-station-kpi",
            "children"
        ),

        Output(
            "stations-start-chart",
            "figure"
        ),

        Output(
            "stations-end-chart",
            "figure"
        ),

        Input(
            "stations-gender-filter",
            "value"
        ),

        Input(
            "stations-user-filter",
            "value"
        )
    )
    def update_stations(
        selected_gender,
        selected_user
    ):

        filtered_df = filter_dataframe(
            df,
            selected_gender,
            selected_user
        )

        station_counts = (
            filtered_df
            .dropna(
                subset=["start_station_name"]
            )
            .groupby(
                "start_station_name"
            )["trip_id"]
            .nunique()
            .sort_values(
                ascending=False
            )
        )

        if station_counts.empty:
            popular_station = "N/A"
        else:
            popular_station = station_counts.index[0]

        start_fig = create_start_station_chart(
            filtered_df
        )

        end_fig = create_end_station_chart(
            filtered_df
        )

        return (
            popular_station,
            start_fig,
            end_fig
        )