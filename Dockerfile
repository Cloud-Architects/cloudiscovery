FROM python:3.7-slim as aws-discover-network

LABEL maintainer_1="https://github.com/leandrodamascena/"
LABEL maintainer_2="https://github.com/meshuga"
LABEL Project="https://github.com/leandrodamascena/aws-network-discovery"

WORKDIR /opt/aws-discover-network

RUN apt-get update -y
RUN apt-get install -y awscli graphviz
RUN apt-get install -y bash

COPY . /opt/aws-discover-network

RUN pip install -r requirements.txt

RUN bash