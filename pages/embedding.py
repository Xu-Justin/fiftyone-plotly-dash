import fiftyone as fo
import fiftyone.brain as fob
import pandas as pd
import math

def compute_embeddings(dataset):
    return fob.compute_visualization(
        dataset,
        num_dims=2,
        brain_key="image_embeddings",
        verbose=True,
        seed=51,
        patches_field="ground_truth"
    ).points
    
def create_dataframe(dataset):
    embeddings = compute_embeddings(dataset)
    
    df = pd.DataFrame(columns=['index', 'uniqueness', 'label','sqrt_area','embeddings_x', 'embeddings_y'])  
    
    index = 0
    for sample in dataset:
        for detection in sample.ground_truth.detections:
            print(detection)
            df.loc[index] = [index, sample.uniqueness, detection.label, math.sqrt(detection.area), embeddings[index,0], embeddings[index, 1]]
            index += 1
            
    return df

def main(name):
    if name not in fo.list_datasets():
        message = f'Dataset {name} is not in list.'
    else:
        dataset = fo.load_dataset(name)
        df = create_dataframe(dataset)
        df.to_pickle(name)
        message = 'Saved embedding to {name}.'
    
    print(message)
    return message
        
import dash
dash.register_page(__name__, path_template="/embedding/<name>")

def layout(name=None):
    print(f'Computing embedding for {name}')
    if name is not None:
        return main(name)