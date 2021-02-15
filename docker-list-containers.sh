#!/bin/bash

echo "list of ai4eu sudoku containers:"
docker container list --all --filter name=ai4eu-sudoku-*
