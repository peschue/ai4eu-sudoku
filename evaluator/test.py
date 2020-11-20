#!/usr/bin/env python3

import logging
import grpc
import sys
import json

import sudoku_design_evaluator_pb2_grpc
import sudoku_design_evaluator_pb2

configfile = "config.json"
config = json.load(open(configfile, 'rt'))

logging.basicConfig(level=logging.INFO)

def main():
   channel = grpc.insecure_channel('localhost:'+str(config['grpcport']))
   encoderstub = sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluationProblemEncoderStub(channel)
   decoderstub = sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluationResultDecoderStub(channel)

   # test evaluateSudokuDesign(...): convert a partial Sudoku field into an ASP Program
   evaluationjob = sudoku_design_evaluator_pb2.SudokuDesignEvaluationJob()
   # dummy field
   evaluationjob.field.extend([ idx % 10 for idx in range(0,81) ])

   solverjob = encoderstub.evaluateSudokuDesign(evaluationjob)
   logging.info("got solverjob response '%s'", solverjob)

   # test processEvaluationResult(...): convert a set of answer sets into a design evaluation result
   # TODO

main()
