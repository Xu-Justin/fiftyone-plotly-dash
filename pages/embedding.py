import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import config

def create_figure(df, min_uniqueness, max_uniqueness, min_sqrt_area, max_sqrt_area):
    mask = (df['uniqueness'] >= min_uniqueness) & (df['uniqueness'] <= max_uniqueness) & (df['sqrt_area'] >= min_sqrt_area) & (df['sqrt_area'] <= max_sqrt_area)
    fig = px.scatter(df[mask], x='embeddings_x', y='embeddings_y', color='label', size='sqrt_area', custom_data=['id'], hover_data=['uniqueness'])
    figure = go.FigureWidget(fig)
    figure.update_layout(
        autosize=True,
        width=1080,
        height=566,
    )
    return figure

df = None

def main(name):

    file_path = f'{name}.pickle'
    if not os.path.exists(file_path): requests.post(url=f'{config.url}:{config.port["flask"]}/compute', json={'name':name})

    global df
    df = pd.read_pickle(file_path)
    uniqueness_range = (0, 1)
    sqrt_area_range = (0, df['sqrt_area'].max())

    figure = create_figure(df, uniqueness_range[0], uniqueness_range[1], sqrt_area_range[0], sqrt_area_range[1])

    return dash.html.Div(children=[
        dash.html.H3('Embedding Visualization'),
        dash.dcc.Graph(
            id='graph',
            figure=figure
        ),
        dash.html.P(f'{name}', id='name'),
        dash.html.P(id='num_sample'),
        dash.html.P('Filter by uniqueness:'),
        dash.dcc.RangeSlider(
            id='uniqueness-slider',
            min=0, max=1, step=0.001,
            marks={0: '0', 1: '1'},
            value=[0, 1]
        ),
        dash.html.P('Filter by sqrt area:'),
        dash.dcc.RangeSlider(
            id='sqrt-area-slider',
            min=0, max=df['sqrt_area'].max(), step=df['sqrt_area'].max()/1000,
            marks={0: '0', df['sqrt_area'].max(): f'{df["sqrt_area"].max()}'},
            value=[0, df['sqrt_area'].max()]
        ),
    ])        

@dash.callback(
    dash.Output(component_id='graph', component_property='figure'), 
    dash.Input(component_id='uniqueness-slider', component_property='value'),
    dash.Input(component_id='sqrt-area-slider', component_property='value'),
)
def update_figure(uniqueness_slider_range, sqrt_area_slider_range):
    global_uniqueness_range = uniqueness_slider_range
    global_sqrt_area_range = sqrt_area_slider_range
    figure = create_figure(df, global_uniqueness_range[0], global_uniqueness_range[1], global_sqrt_area_range[0], global_sqrt_area_range[1])
    print(f'Updated uniquesness range to {global_uniqueness_range}')
    print(f'Updated sqrt area range to {global_sqrt_area_range}')
    return figure

@dash.callback(
    dash.Output(component_id='num_sample', component_property='children'),
    dash.Input(component_id='name', component_property='children'),
    dash.Input(component_id='graph', component_property='selectedData')
)
def update(name, input_value):
    if input_value is None: return f'No sample selected.'
    ids = []
    points = input_value['points']
    for point in points:
        id = point['customdata'][0]
        ids.append(id)
    requests.post(
        url = f'{config.url}:{config.port["flask"]}/fiftyone/update',
        json = {
            'name' : name,
            'ids' : ids
        }
    )
    return f'Number of patches: {len(ids)}'
    
dash.register_page(__name__, path_template="/embedding/<name>")

def layout(name=None):
    print(f'Dash embedding {name}')
    if name is not None:
        return main(name)