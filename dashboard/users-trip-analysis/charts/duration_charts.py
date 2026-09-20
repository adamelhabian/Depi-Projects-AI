import plotly.express as px


def create_user_duration_chart(df):

    duration_by_user = (
        df.groupby("user_type")["duration_min"]
        .mean()
        .reset_index()
    )

    duration_by_user.columns = [
        "user_type",
        "avg_duration"
    ]

    fig = px.bar(
        duration_by_user,
        x="user_type",
        y="avg_duration",
        title="Average Trip Duration by User Type",
        labels={
            "user_type": "User Type",
            "avg_duration": "Average Duration (Minutes)"
        },
        text_auto=".2f"
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig


def create_hour_duration_chart(df):

    duration_by_hour = (
        df.groupby("start_hour")["duration_min"]
        .mean()
        .reset_index()
        .sort_values("start_hour")
    )

    duration_by_hour.columns = [
        "hour",
        "avg_duration"
    ]

    fig = px.line(
        duration_by_hour,
        x="hour",
        y="avg_duration",
        markers=True,
        title="Average Trip Duration by Hour",
        labels={
            "hour": "Start Hour",
            "avg_duration": "Average Duration (Minutes)"
        }
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    return fig