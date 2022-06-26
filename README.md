# fiftyone-plotly-dash

This repository integrates [fiftyone image embeddings](https://voxel51.com/docs/fiftyone/tutorials/image_embeddings.html) to web browser using [plotly-dash](https://plotly.com/dash/), so that user no longer need to use jupyter notebook or jupyter lab to preview and interact with image embeddings plot.

## Usage

The program `app_flask.py` responsible to serve fiftyone application, while the program `app_dash.py` responsible to serve plotly plot on dash server. Both programs need to be run parallely in order to work as it should.

Run the following command on terminal to clone this repository, then execute `run.sh` to run `app_flask.py` and `app_dash.py` in parallel.

```
git clone https://github.com/Xu-Justin/fiftyone-plotly-dash.git
cd fiftyone-plotly-dash
./run.sh
```

## API

**`GET`** `localhost:6001/embedding/<name>`

> Display image embeddings plot of `<name>`.

<br>

**`GET`** `localhost:6001/fiftyone/<name>`

> Display selected image embeddings scatter of `<name>` on fiftyone interface.

<br>

**`POST`** `localhost:6001/compute`

> This API is expected to receive a JSON data with key `{name:str}`.

> Compute image embeddings of `<name>` and saved the result to `<name>.pickle`.

> This API is automatically called when **`GET`** `localhost:6001/embedding/<name>` couldn't find `<name>.pickle`.

<br>

**`POST`** `localhost:6001/fiftyone/update`

> This API is expected to receive a JSON data with key `{name:str, ids:list_of_id}`.

> Update fiftyone view of <name> to only contains <ids> images.

## Docker

It is recommended to do the inference inside a docker container to prevent version conflicts. The container image for this project is available on  [Docker Hub](https://hub.docker.com/repository/docker/jstnxu/fiftyone-plotly-dash) and can be pulled using the following commands.

```
docker pull jstnxu/fiftyone-plotly-dash
```

The following commands will run the docker image.
  
```
docker run -it --ipc=host -v <local_fiftyone>:/root/.fiftyone/ -p <local_port>:6000-6003 --rm jstnxu/fiftyone-plotly-dash
```

---
  
This project was developed as part of Nodeflux Internship x Kampus Merdeka.
