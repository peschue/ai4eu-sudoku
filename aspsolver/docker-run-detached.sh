#!/bin/bash

docker run --name ai4eu-sudoku-aspsolver -it --publish=8003:8003 -d ai4eu-sudoku-aspsolver:$ASPSOLVER_IMAGE_VERSION
