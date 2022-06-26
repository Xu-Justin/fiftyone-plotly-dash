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
    
    df = pd.DataFrame(columns=['id', 'uniqueness', 'label', 'area', 'sqrt_area','embeddings_x', 'embeddings_y'])  
    
    index = 0

    for sample in dataset:

        try: uniqueness = sample.uniqueness
        except: uniqueness = 0

        for detection in sample.ground_truth.detections:

            id = detection.id
            
            try: label = detection.label
            except: label = ''

            try: area = detection.area
            except: area = 1

            embeddings_x = embeddings[index, 0]
            embeddings_y = embeddings[index, 1]

            df.loc[index] = [id, uniqueness, label, area, math.sqrt(area), embeddings_x, embeddings_y]

            index += 1
            
    return df