#!/usr/bin/env python3
 
# orchestrate the sudoku example
#
# pseudocode (simple nonparallel case)
# 
# while true:
#   guijob = gui.requestSudokuEvaluation(dummy1)
#   solverjob = evaluator.evaluateSudokuDesign(guijob)
#   aspresult = aspsolver.solve(solverjob)
#   evalresult = evaluator.processEvaluationResult(aspresult)
#   (dummy2 = )gui.processEvaluationResult(evalresult)

import os
import logging
import json
import time
import grpc
import sys
import traceback

logging.basicConfig(level=logging.DEBUG)

logging.info("importing generated protobuf modules")

import google.protobuf.empty_pb2
import sudoku_gui_pb2
import sudoku_gui_pb2_grpc
import sudoku_design_evaluator_pb2_grpc
import asp_pb2_grpc

configfile = "config.json"
config = json.load(open(configfile, 'rt'))

def main():
    gui_channel = grpc.insecure_channel('localhost:'+str(config['gui-grpcport']))
    gui_stub = sudoku_gui_pb2_grpc.SudokuGUIStub(gui_channel)

    evaluator_channel = grpc.insecure_channel('localhost:'+str(config['designevaluator-grpcport']))
    evaluator_stub = sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluatorStub(evaluator_channel)

    aspsolver_channel = grpc.insecure_channel('localhost:'+str(config['aspsolver-grpcport']))
    aspsolver_stub = asp_pb2_grpc.OneshotSolverStub(aspsolver_channel)

    while True:
      try:
        logging.info("calling SudokuGUI.requestSudokuEvaluation() with empty dummy")
        dummy1 = google.protobuf.empty_pb2.Empty()
        guijob = gui_stub.requestSudokuEvaluation(dummy1)

        logging.info("calling SudokuDesignEvaluator.evaluateSudokuDesign() with guijob")
        solverjob = evaluator_stub.evaluateSudokuDesign(guijob)

        logging.info("calling OneshotSolver.solve() with parameters %s", solverjob.parameters)
        aspresult = aspsolver_stub.solve(solverjob)

        logging.info("calling SudokuDesignEvaluator.processEvaluationResult() with %d answer sets and description %s",
          len(aspresult.answers), aspresult.description)
        evalresult = evaluator_stub.processSolverResult(aspresult)

        logging.info("calling SudokuGUI.processEvaluationResult() with status %d, len(solution)=%d, len(minimal_unsolvable)=%s",
          evalresult.status, len(evalresult.solution), len(evalresult.inconsistency_involved))
        dummy2 = gui_stub.processEvaluationResult(evalresult)

      except Exception:
        logging.error("exception (retrying after 2 seconds): %s", traceback.format_exc())
        # do not spam
        time.sleep(2)

main()
