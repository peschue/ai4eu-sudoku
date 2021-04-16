# debian with Python preinstalled
FROM python:3.7-slim-buster

# upgrade and install some helpful packages (not strictly required)
#
# ENV DEBIAN_FRONTEND noninteractive
# ENV TERM linux
# RUN set -ex \
#     && apt-get update -yqq \
#     && apt-get upgrade -yqq \
#     && apt-get install -yqq --no-install-recommends \
#         curl less nano vi

# copy dependency information
COPY requirements.txt /

# install Python packages
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r /requirements.txt

# copy sources
RUN mkdir /app
RUN mkdir /app/templates
COPY gui.css gui.js config.json sudoku-gui.proto server.py /app/
COPY templates/* /app/templates/

# adhere to container specification by also providing these two files
COPY sudoku-gui.proto /model.proto
COPY license.json /license.json

WORKDIR /app

# compile protobuf
RUN python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto

EXPOSE 8061 8062

# run server with default Python log level "debug"
#ENV GRPC_TRACE=channel,call-error,client_channel,connectivity_state
#ENV GRPC_VERBOSITY=INFO
CMD uvicorn server:app --host 0.0.0.0 --port 8062 --log-level ${PYTHON_LOGLEVEL:-debug}
