#!/bin/bash

docker container kill $(docker container ls -q --filter name=ai4eu-sudoku-aspsolver)
docker container rm ai4eu-sudoku-aspsolver