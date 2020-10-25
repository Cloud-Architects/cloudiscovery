FROM python:3.8-slim as cloudiscovery

LABEL maintainer_1="https://github.com/leandrodamascena/"
LABEL maintainer_2="https://github.com/meshuga"
LABEL Project="https://github.com/Cloud-Architects/cloudiscovery"

WORKDIR /opt/cloudiscovery

RUN apt-get update -y
RUN apt-get install -y awscli graphviz
RUN apt-get install -y bash

COPY . /opt/cloudiscovery

RUN pip install -r requirements.txt

RUN bash