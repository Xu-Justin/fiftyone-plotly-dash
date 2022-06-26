FROM python:3.9.13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && \
    apt-get install -y git vim libgtk2.0-dev zip unzip && \
    rm -rf /var/cache/apk/*

COPY requirements.txt /
RUN pip --no-cache-dir install fiftyone==0.16.5
RUN pip --no-cache-dir install -r /requirements.txt

WORKDIR /local
COPY app_flask.py app_dash.py config.py utils.py run.sh ./
COPY pages/embedding.py ./pages/

EXPOSE 6000-6003
CMD ./run.sh