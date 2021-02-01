#!/bin/sh

docker tag ai4eu-sudoku-aspsolver:$ASPSOLVER_IMAGE_VERSION $REMOTE_REPO/tutorials/sudoku/ai4eu-sudoku-aspsolver:$ASPSOLVER_IMAGE_VERSION
docker push $REMOTE_REPO/tutorials/sudoku/ai4eu-sudoku-aspsolver:$ASPSOLVER_IMAGE_VERSION
