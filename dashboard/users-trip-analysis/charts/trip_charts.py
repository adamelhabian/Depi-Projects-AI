import plotly.express as px


# def create_monthly_trips_chart(df):

#     monthly_trips = (
#         df.groupby(
#             ["year", "month", "month_name"]
#         )
#         .size()
#         .reset_index(name="trips")
#         .sort_values(
#             ["year", "month"]
#         )
#     )

#     fig = px.line(
#         monthly_trips,
#         x="month_name",
#         y="trips",
#         markers=True,
#         title="Trips by Month",
#         labels={
#             "month_name": "Month",
#             "trips": "Number of Trips"
#         }
#     )

#     fig.update_layout(
#         template="plotly_white",
#         hovermode="x unified"
#     )

#     return fig


def create_daily_trips_chart(df):

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    daily_trips = (
        df["day_name"]
        .value_counts()
        .reindex(day_order)
        .reset_index()
    )

    daily_trips.columns = [
        "day_name",
        "trips"
    ]

    fig = px.bar(
        daily_trips,
        x="day_name",
        y="trips",
        title="Trips by Day of Week",
        labels={
            "day_name": "Day",
            "trips": "Number of Trips"
        }
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig