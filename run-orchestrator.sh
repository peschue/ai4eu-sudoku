#!/bin/echo must be run in bash with . 

conda activate ai4eusudoku

(
    pushd orchestrator
    python3 orchestrator.py
    popd
)
