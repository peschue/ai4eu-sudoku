#!/bin/bash

set -ex

if test "x$GUI_IMAGE_VERSION" == "x"; then
	echo "variable GUI_IMAGE_VERSION is empty, PLEASE RUN ./versions.sh!"
	exit -1
fi

for component in gui evaluator aspsolver; do
	pushd $component
	./docker-run-detached.sh
	popd
done
