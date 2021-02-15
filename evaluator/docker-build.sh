#!/bin/bash

if test "x$EVALUATOR_IMAGE_VERSION" == "x"; then
	echo "variable EVALUATOR_IMAGE_VERSION is empty, PLEASE RUN 'source versions.sh'"
	exit -1
fi

docker build -t ai4eu-sudoku-designevaluator:$EVALUATOR_IMAGE_VERSION .
