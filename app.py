from dash import Dash, html, dcc
import dash

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
	dash.page_container
])

if __name__ == '__main__':
	app.run_server()