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

    file_path = f'{config.cache_folder}/{name}.pickle'
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
                dbc.Button("Select All", color="primary", className="me-3", id='select-all'),
                className = 'd-flex justify-content-end'
            ),
            dbc.Container(
                children = [
                    dash.html.Pre('Dataset Name: '),
                    dash.html.Pre(f'{name}', id='name'),
                ],
                className = 'd-flex justify-content-start mx-3'
            ),
            dbc.Container(
                children = [
                    dash.html.P(id='num_sample'),
                ],
                className = 'mx-3 mb-3'
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
            dbc.Button("Open Fiftyone", outline=True, color="secondary", className="m-3", href=f'{config.url}:{config.port["flask"]}/fiftyone/{name}', external_link=True, target='_blank'),
            dash.html.P(id='dummy-1'),
            dash.html.P(id='dummy-2'),
        ],
        className = 'p-5 vh-100 vw-100'
    )

@dash.callback(
    dash.Output(component_id='graph', component_property='figure'), 
    dash.Input(component_id='select-all', component_property='n_clicks'),
    dash.Input(component_id='uniqueness-slider', component_property='value'),
    dash.Input(component_id='sqrt-area-slider', component_property='value'),
)
def callback_select_all(n_clicks, uniqueness_range, sqrt_area_range):
    figure = create_figure(df, uniqueness_range[0], uniqueness_range[1], sqrt_area_range[0], sqrt_area_range[1])
    print(f'Updated uniquesness range to {uniqueness_range}')
    print(f'Updated sqrt area range to {sqrt_area_range}')
    return figure

@dash.callback(
    dash.Output(component_id='num_sample', component_property='children'),
    dash.Input(component_id='name', component_property='children'),
    dash.Input(component_id='graph', component_property='selectedData'),
    dash.Input(component_id='graph', component_property='figure'),
)
def callback_graph(name, selected_data, figure):
    message_no_sample = f'No sample selected.'
    ids = []

    if not isinstance(dash.ctx.triggered_prop_ids, dash._utils.AttributeDict): return message_no_sample

    if 'graph.selectedData' in dash.ctx.triggered_prop_ids:
        for point in selected_data['points']:
            id = point['customdata'][0]
            ids.append(id)
    elif 'graph.figure' in dash.ctx.triggered_prop_ids:
        for data in figure['data']:
            for custom_data in data['customdata']:
                id = custom_data[0]
                ids.append(id)
    else: return message_no_sample

    if len(ids):
        fiftyone_update(name, ids)
        return f'Number of patches: {len(ids)}'
    else: return message_no_sample

def fiftyone_update(name, ids):
    requests.post(
        url = f'{config.url}:{config.port["flask"]}/fiftyone/update',
        json = {
            'name' : name,
            'ids' : ids
        }
    )
    print(f'Updated fiftyone dataset {name} to {len(ids)} patches')

dash.register_page(__name__, path_template="/embedding/<name>")

def layout(name=None):
    print(f'Dash embedding {name}')
    if name is not None:
        return main(name)