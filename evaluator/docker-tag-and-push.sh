#!/bin/sh

# define versions to be used
. ../versions.sh

docker tag ai4eu-sudoku-designevaluator:$EVALUATOR_IMAGE_VERSION $REMOTE_REPO/tutorials/sudoku/ai4eu-sudoku-designevaluator:$EVALUATOR_IMAGE_VERSION
docker push $REMOTE_REPO/tutorials/sudoku/ai4eu-sudoku-designevaluator:$EVALUATOR_IMAGE_VERSION
