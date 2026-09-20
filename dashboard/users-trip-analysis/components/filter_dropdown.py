from dash import dcc


def create_filter_dropdown(
    filter_id,
    label,
    options,
    value=None,
    multi=False
):

    return dcc.Dropdown(
        id=filter_id,
        options=[
            {
                "label": option,
                "value": option
            }
            for option in options
        ],
        value=value,
        multi=multi,
        clearable=True,
        placeholder=f"Select {label}...",
        style={
            "width": "100%"
        }
    )