# debian with Python preinstalled
FROM python:3.7-slim-buster

# copy dependency information
COPY requirements.txt /

# install Python packages
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r /requirements.txt

# install some helpful packages (not strictly required)
#
# RUN set -ex \
#     && apt-get install -yqq --no-install-recommends \
#         curl less nano vi

# copy sources
RUN mkdir /app
COPY config.json sudoku-design-evaluator.proto server.py /app/

# adhere to container specification by also providing these two files
COPY sudoku-design-evaluator.proto /model.proto
COPY license.json /license.json

WORKDIR /app

# compile protobuf
RUN python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto

# tell docker that this container has port 8002 active
EXPOSE 8061

# run server
CMD python3 server.py
