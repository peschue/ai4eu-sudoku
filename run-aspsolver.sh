#!/bin/echo must be run in bash with . 

conda activate ai4eusudoku

(
    pushd aspsolver
    python3 server.py
)