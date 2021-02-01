#!/bin/bash

docker run --rm --name ai4eu-sudoku-aspsolver -it --publish=8003:8003 ai4eu-sudoku-aspsolver:$ASPSOLVER_IMAGE_VERSION /bin/bash
