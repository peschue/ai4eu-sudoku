# debian with Python preinstalled
FROM python:3.7-slim-buster

ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# install required packages for building clingo
RUN set -ex \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq git build-essential cmake bison re2c python3-dev \
    && apt-get clean

# copy dependency information
COPY requirements.txt /

# install Python packages
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r /requirements.txt

# install some helpful packages (not strictly required)
#
# RUN set -ex \
#     && apt-get install -yqq --no-install-recommends \
#         curl less nano vi

# build clingo
ENV CLINGO_TAG_VERSION v5.2.2
RUN mkdir -p /opt/clingo
WORKDIR /opt/clingo
RUN set -ex \
    && git init \
    && git remote add origin https://github.com/potassco/clingo.git \
    && git fetch origin ${CLINGO_TAG_VERSION} \
    && git pull origin ${CLINGO_TAG_VERSION} \
    && git submodule update --init --recursive
RUN set -ex \
    && cmake -H/opt/clingo -B/opt/clingo -DCMAKE_BUILD_TYPE=release \
    && cmake --build /opt/clingo

ENV PYTHONPATH /opt/clingo/bin/python/

# copy sources
RUN mkdir /app
COPY config.json asp.proto server.py /app/

# adhere to container specification by also providing these two files
COPY asp.proto /model.proto
COPY license.json /license.json

WORKDIR /app

# compile protobuf
RUN python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. asp.proto

EXPOSE 8061

# run server
CMD python3 server.py
