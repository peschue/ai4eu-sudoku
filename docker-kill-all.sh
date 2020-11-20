#!/bin/bash

# attempt to kill all, even if some fail

for component in gui evaluator aspsolver; do
	pushd $component
	./docker-kill.sh
	popd
done
