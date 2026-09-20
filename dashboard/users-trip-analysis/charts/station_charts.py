import plotly.express as px


def create_start_station_chart(df):

    start_station_counts = (
        df.dropna(
            subset=["start_station_name"]
        )
        .groupby("start_station_name")["trip_id"]
        .nunique()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    start_station_counts.columns = [
        "station",
        "trips"
    ]

    fig = px.bar(
        start_station_counts,
        x="trips",
        y="station",
        orientation="h",
        title="Top 10 Start Stations",
        labels={
            "station": "Start Station",
            "trips": "Number of Trips"
        },
        text_auto=True
    )

    fig.update_layout(
        template="plotly_white",
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    return fig


def create_end_station_chart(df):

    end_station_counts = (
        df.dropna(
            subset=["end_station_name"]
        )
        .groupby("end_station_name")["trip_id"]
        .nunique()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    end_station_counts.columns = [
        "station",
        "trips"
    ]

    fig = px.bar(
        end_station_counts,
        x="trips",
        y="station",
        orientation="h",
        title="Top 10 End Stations",
        labels={
            "station": "End Station",
            "trips": "Number of Trips"
        },
        text_auto=True
    )

    fig.update_layout(
        template="plotly_white",
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    return fig