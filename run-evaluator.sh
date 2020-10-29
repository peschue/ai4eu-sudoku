#!/bin/echo must be run in bash with . 

conda activate ai4eusudoku

(
    pushd evaluator
    python3 server.py
)