import dash
import config

app = dash.Dash(__name__, use_pages=True)
app.layout = dash.html.Div([
	dash.page_container
])

if __name__ == '__main__':
	app.run_server(host=config.host, port=config.port['dash'])