#!/bin/bash

set -ex

for component in gui evaluator aspsolver; do
	pushd $component
	./docker-run-detached.sh
	popd
done
