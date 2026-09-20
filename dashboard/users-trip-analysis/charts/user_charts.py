import plotly.express as px


def create_user_type_chart(df):

    user_counts = (
        df.groupby("user_type")["trip_id"]
        .nunique()
        .reset_index()
    )

    user_counts.columns = [
        "user_type",
        "trips"
    ]

    fig = px.bar(
        user_counts,
        x="user_type",
        y="trips",
        title="Trips by User Type",
        labels={
            "user_type": "User Type",
            "trips": "Number of Trips"
        },
        text_auto=True
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig


def create_gender_user_chart(df):

    gender_user = (
        df.dropna(
            subset=[
                "user_type",
                "member_gender"
            ]
        )
        .groupby(
            [
                "user_type",
                "member_gender"
            ]
        )["trip_id"]
        .nunique()
        .reset_index()
    )

    gender_user.columns = [
        "user_type",
        "gender",
        "trips"
    ]

    fig = px.bar(
        gender_user,
        x="user_type",
        y="trips",
        color="gender",
        barmode="group",
        title="Trips by Gender and User Type",
        labels={
            "user_type": "User Type",
            "trips": "Number of Trips",
            "gender": "Gender"
        }
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig