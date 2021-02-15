#!/bin/bash

docker run --name ai4eu-sudoku-designevaluator --publish=8002:8002 -d ai4eu-sudoku-designevaluator:$EVALUATOR_IMAGE_VERSION
