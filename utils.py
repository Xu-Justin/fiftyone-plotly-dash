import fiftyone as fo

def create_quickstart():
    import fiftyone.zoo as foz
    return foz.load_zoo_dataset("quickstart")

def create(name):
    return fo.Dataset(name)

def load(name):
    return fo.load_dataset(name)

def delete(name):
    dataset = load(name)
    dataset.delete()

def ls():
    print(fo.list_datasets())