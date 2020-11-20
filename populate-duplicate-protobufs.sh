#!/bin/bash

# This script is required because docker does not permit to follow symlinks to parent directories.
# Therefore we have to copy and cannot symlink .proto files.

set -ex

cp aspsolver/asp.proto evaluator/
cp aspsolver/asp.proto gui/
cp aspsolver/asp.proto orchestrator/

cp evaluator/sudoku-design-evaluator.proto gui/
cp evaluator/sudoku-design-evaluator.proto orchestrator/

cp gui/sudoku-gui.proto orchestrator/
