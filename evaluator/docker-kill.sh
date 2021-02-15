#!/bin/bash

docker container kill $(docker container ls -q --filter name=ai4eu-sudoku-designevaluator)
docker container rm ai4eu-sudoku-designevaluator