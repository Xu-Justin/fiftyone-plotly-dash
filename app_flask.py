import fiftyone as fo
from flask import Flask, render_template, request, redirect, url_for
import config, utils

app = Flask(__name__)
dataset = fo.Dataset()
session = None

@app.route('/fiftyone/<name>', methods=['GET'])
def preview_fiftyone(name):
    return redirect(f'{config.url}:{config.port["fiftyone"]}/datasets/{name}')

@app.route('/embedding/<name>', methods=['GET'])
def preview_embedding(name):
    return redirect(f'{config.url}:{config.port["dash"]}/embedding/{name}')

@app.route('/compute', methods=['POST'])
def compute():
    data = request.get_json()
    name = data['name']

    dataset =  fo.load_dataset(name)
    df = utils.create_dataframe(dataset)
    save_path = f'{name}.pickle'
    df.to_pickle(save_path)

    print(f'Saved computation to {save_path}')
    return '', 204

@app.route('/fiftyone/update', methods=['POST'])
def fiftyone_load():
    data = request.get_json()
    name = data['name']
    ids = data['ids']

    global dataset, session
    dataset = fo.load_dataset(name)
    stage = fo.Select(ids)
    view = dataset.to_patches('ground_truth').add_stage(stage)
    session.view = view
    
    print(f'Updated view of dataset {name} to {len(ids)} patches.')
    return '', 204

if __name__ == '__main__':
    session = fo.launch_app(dataset, address=config.address, port=config.port['fiftyone'], remote=True)
    app.run(host=config.host, port=config.port['flask'])
    # app.run(host='0.0.0.0', port='6000')