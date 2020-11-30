#!/bin/echo must be run in bash with . 

# This script is maybe the easiest way to run each component outside of docker and to run the orchestrator.
#
# The orchestrator just requires grpcio-tools and protobuf.

conda create -n ai4eusudoku -c conda-forge fastapi protobuf grpcio-tools uvicorn 'python>=3.5' clingo
