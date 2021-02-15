#!/bin/bash

if test "x$GUI_IMAGE_VERSION" == "x"; then
	echo "variable GUI_IMAGE_VERSION is empty, PLEASE RUN 'source versions.sh'"
	exit -1
fi

docker build -t ai4eu-sudoku-gui:$GUI_IMAGE_VERSION .
