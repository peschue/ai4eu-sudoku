#!/bin/bash

docker run --rm --name ai4eu-sudoku-gui -it --publish=8000:8000 --publish=8001:8001 ai4eu-sudoku-gui /bin/bash
