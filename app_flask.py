import fiftyone as fo
from flask import Flask, render_template, request, redirect, url_for
import config, utils
import os, shutil

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
    save_path = f'{config.cache_folder}/{name}.pickle'
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

@app.route('/delete/cache', methods=['POST'])
def delete_cache():
    shutil.rmtree(f'{config.cache_folder}')
    os.makedirs(f'{config.cache_folder}')
    print(f'Deleted cache folder.')
    return '', 204

if __name__ == '__main__':
    session = fo.launch_app(dataset, address=config.address, port=config.port['fiftyone'], remote=True)
    app.run(host=config.host, port=config.port['flask'])