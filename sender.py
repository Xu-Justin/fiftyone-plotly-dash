import requests
import config

def get(url):
    return requests.get(url)

def post(url, data):
    requests.post(url=url, json=data)

def preview_fiftyone(name):
    get(
        url = f'{config.url}:{config.port["flask"]}/fiftyone/{name}'
    )

def preview_embedding(name):
    get(
        url = f'{config.url}:{config.port["flask"]}/embedding/{name}'
    )

def compute(name):
    post(
        url = f'{config.url}:{config.port["flask"]}/compute',
        data = {
            'name' : name
        }
    )

def fiftyone_load(name, ids):
    post(
        url = f'{config.url}:{config.port["flask"]}/fiftyone/load',
        data = {
            'name' : name,
            'ids' : ids
        }
    )

if __name__ == '__main__':
    compute('quickstart')
    preview_embedding('quickstart')
    preview_fiftyone('quickstart')
    # fiftyone_load('quickstart', [''])