import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
import requests
import os
import config

def create_figure(df, min_uniqueness, max_uniqueness, min_sqrt_area, max_sqrt_area):
    mask = (df['uniqueness'] >= min_uniqueness) & (df['uniqueness'] <= max_uniqueness) & (df['sqrt_area'] >= min_sqrt_area) & (df['sqrt_area'] <= max_sqrt_area)
    fig = px.scatter(df[mask], x='embeddings_x', y='embeddings_y', color='label', size='sqrt_area', custom_data=['id'], hover_data=['uniqueness'])
    figure = go.FigureWidget(fig)
    figure.update_layout(
        dragmode='lasso'
    )
    return figure

df = None

def main(name):

    file_path = f'{name}.pickle'
    if not os.path.exists(file_path): requests.post(url=f'{config.url}:{config.port["flask"]}/compute', json={'name':name})

    global df
    df = pd.read_pickle(file_path)
    uniqueness_range = (0, 1)
    sqrt_area_range = (0, math.ceil(df['sqrt_area'].max()))

    figure = create_figure(df, uniqueness_range[0], uniqueness_range[1], sqrt_area_range[0], sqrt_area_range[1])

    return dbc.Container(
        children = [
            dash.html.H1('Embedding Visualization', style = {'text-align':'center'}),
            dbc.Container(
                children = [
                    dash.html.P(
                        '''
                        Each node in this graph represents a bounding box in the dataset.
                        Use 'box select' or 'lasso select' to select nodes. Double click on a label to excluded the other label.
                        The slider will filter nodes that do not meet the criteria. Note that the slider don't update the selection.
                        Selected nodes on this graph can be previewed on Fiftyone through the button on the bottom of this page.
                        '''
                    ),
                ],
                className = 'm-3'
            ),
            dash.html.Div(
                dash.dcc.Graph(
                    id='graph',
                    figure=figure,
                    responsive=True,
                    style={'width' : '100%', 'height': '100%'}
                ),
                style={'width' : '100%', 'height': '60%'}
            ),
            dbc.Container(
                children = [
                    dash.html.P(f'{name}', id='name'),
                    dash.html.P(id='num_sample'),
                ],
                className = 'm-3'
            ),
            dbc.Container(
                children = [
                    dash.html.B('Filter by Uniqueness'),
                    dash.dcc.RangeSlider(
                        id='uniqueness-slider',
                        min=uniqueness_range[0], max=uniqueness_range[1], step=(uniqueness_range[1]-uniqueness_range[0])/1000,
                        marks={uniqueness_range[0]: uniqueness_range[0], uniqueness_range[1]: uniqueness_range[1]},
                        value=[uniqueness_range[0], uniqueness_range[1]]
                    )
                ],
                className = 'm-3'
            ),
            dbc.Container(
                children = [
                    dash.html.B('Filter by Sqrt Area'),
                    dash.dcc.RangeSlider(
                        id='sqrt-area-slider',
                        min=sqrt_area_range[0], max=sqrt_area_range[1], step=(sqrt_area_range[1]-sqrt_area_range[0])/1000,
                        marks={sqrt_area_range[0]: sqrt_area_range[0], sqrt_area_range[1]: sqrt_area_range[1]},
                        value=[sqrt_area_range[0], sqrt_area_range[1]]
                    ),
                ],
                className = 'm-3'
            ),
            dbc.Button('Open Fiftyone', color='light', className='m-3', href=f'{config.url}:{config.port["flask"]}/fiftyone/{name}', external_link=True, target='_blank'),
        ],
        className = 'p-5 vh-100 vw-100'
    )

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