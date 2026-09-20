from dash import html


def create_kpi_card(title, value, value_id=None):
    return html.Div(
        children=[
            html.P(
                title,
                style={
                    "fontSize": "16px",
                    "marginBottom": "5px"
                }
            ),

            html.H2(
                value,
                id=value_id,
                style={
                    "fontSize": "32px",
                    "margin": "0"
                }
            )
        ],

        style={
            "backgroundColor": "white",
            "padding": "25px",
            "borderRadius": "12px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
            "marginBottom": "25px"
        }
    )