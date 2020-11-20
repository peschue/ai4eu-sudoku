#!/bin/bash

docker run --rm --name ai4eu-sudoku-gui --publish=8000:8000 --publish=8001:8001 -d ai4eu-sudoku-gui
