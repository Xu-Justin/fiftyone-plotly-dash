import fiftyone as fo
from flask import Flask, request, redirect, jsonify
from threading import Timer
from datetime import datetime
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

@app.route('/fiftyone/save/view', methods=['POST'])
def fiftyone_save_session_view():
    global session
    view = session.view
    if type(view) == fo.core.patches.PatchesView:
        view.save()
        print(f'{datetime.now().time()} Saved view {view.name}.')
    return '', 204

def auto_fiftyone_save_session_view(interval):
    Timer(interval, auto_fiftyone_save_session_view, [interval]).start()
    fiftyone_save_session_view()

@app.route('/delete/cache', methods=['POST'])
def delete_cache():
    shutil.rmtree(f'{config.cache_folder}')
    os.makedirs(f'{config.cache_folder}')
    print(f'Deleted cache folder.')
    return '', 204

if __name__ == '__main__':
    session = fo.launch_app(dataset, address=config.address, port=config.port['fiftyone'], remote=True)
    auto_fiftyone_save_session_view(config.auto_save_interval)
    app.run(host=config.host, port=config.port['flask'])