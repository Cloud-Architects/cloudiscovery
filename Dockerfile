FROM python:3.7-slim as cloud-discovery

LABEL maintainer_1="https://github.com/leandrodamascena/"
LABEL maintainer_2="https://github.com/meshuga"
LABEL Project="https://github.com/Cloud-Architects/aws-network-discovery"

WORKDIR /opt/cloud-discovery

RUN apt-get update -y
RUN apt-get install -y awscli graphviz
RUN apt-get install -y bash

COPY . /opt/cloud-discovery

RUN pip install -r requirements.txt

RUN bash