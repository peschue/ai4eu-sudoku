#!/usr/bin/env python3

import logging
import grpc
import sys
import json

import sudoku_gui_pb2
import sudoku_gui_pb2_grpc


logging.basicConfig(level=logging.INFO)

def main():
   # !!! here it is hardcoded to use the external port that ./helper.py assigns to the docker container !!!
   # !!! if you run without docker, you need to use port 8061 !!!
   channel = grpc.insecure_channel('localhost:8001')
   stub = sudoku_gui_pb2_grpc.SudokuGUIStub(channel)

   result = sudoku_gui_pb2.SudokuDesignEvaluationResult()

   # example: unique solution
   result.status = 1
   result.solution.extend([
       ((x+2*y) % 9)+1
       for x in range(1,10)
       for y in range(1,10)
   ])

   response = stub.processEvaluationResult(result)

   logging.info("got response '%s'", response)

main()
