#!/usr/bin/env python3

import logging
import grpc
import sys
import json

import sudoku_design_evaluator_pb2
import sudoku_design_evaluator_pb2_grpc

logging.basicConfig(level=logging.INFO)

def main():
   # !!! here it is hardcoded to use the external port that ./helper.py assigns to the docker container !!!
   # !!! if you run without docker, you need to use port 8061 !!!
   channel = grpc.insecure_channel('localhost:8002')
   stub = sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluatorStub(channel)

   # test evaluateSudokuDesign(...): convert a partial Sudoku field into an ASP Program
   evaluationjob = sudoku_design_evaluator_pb2.SudokuDesignEvaluationJob()
   # dummy field
   evaluationjob.field.extend([ idx % 10 for idx in range(0,81) ])

   solverjob = stub.evaluateSudokuDesign(evaluationjob)
   logging.info("got solverjob response '%s'", solverjob)

   # test processEvaluationResult(...): convert a set of answer sets into a design evaluation result
   # TODO

main()
