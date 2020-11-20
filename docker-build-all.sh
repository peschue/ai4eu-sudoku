#!/bin/bash

set -ex

for component in gui evaluator aspsolver; do
	pushd $component
	./docker-build.sh
	popd
done
