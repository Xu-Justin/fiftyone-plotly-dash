import dash
from dash import html

dash.register_page(__name__, path_template="/report/<report_id>")


def layout(report_id=None):
    print('display')
    return html.Div(
        f"The user requested report ID: {report_id}."
    )