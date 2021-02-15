#!/bin/bash

docker container kill $(docker container ls -q --filter name=ai4eu-sudoku-gui)
docker container rm ai4eu-sudoku-gui