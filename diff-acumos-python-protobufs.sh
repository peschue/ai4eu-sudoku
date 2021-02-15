#!/bin/bash

echo "doing some diff-ing for tracking inconsistencies between Acumos an python versions (eventually there will be only one version)"

diff -c acumos/sudoku-gui.proto gui/sudoku-gui.proto
diff -c acumos/sudoku-design-evaluator.proto evaluator/sudoku-design-evaluator.proto
diff -c acumos/asp.proto aspsolver/asp.proto
