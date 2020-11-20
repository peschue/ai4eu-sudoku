#!/usr/bin/env python3

import logging
import grpc
import sys
import json

import sudoku_gui_pb2_grpc
import sudoku_gui_pb2

configfile = "config.json"
config = json.load(open(configfile, 'rt'))

logging.basicConfig(level=logging.INFO)

def main():
   channel = grpc.insecure_channel('localhost:'+str(config['grpcport']))
   stub = sudoku_gui_pb2_grpc.SudokuDesignEvaluationResultProcessorStub(channel)

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
