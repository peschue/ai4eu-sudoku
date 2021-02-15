#!/bin/bash

if test "x$ASPSOLVER_IMAGE_VERSION" == "x"; then
	echo "variable ASPSOLVER_IMAGE_VERSION is empty, PLEASE RUN 'source versions.sh'"
	exit -1
fi

docker build -t ai4eu-sudoku-aspsolver:$ASPSOLVER_IMAGE_VERSION .
