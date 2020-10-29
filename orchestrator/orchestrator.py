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

sys.path.append('../protobuf/')
# import sudoku_gui_pb2_grpc
# import sudoku_gui_pb2
# import sudoku_design_evaluator_pb2_grpc
# import sudoku_design_evaluator_pb2
# import asp_pb2_grpc
# import asp_pb2
import orchestrator_pb2_grpc
import orchestrator_pb2

configfile = "../config.json"
config = json.load(open(configfile, 'rt'))

def main():
    gui_channel = grpc.insecure_channel('localhost:'+str(config['gui-grpcport']))
    # gui_request_stub = sudoku_gui_pb2_grpc.SudokuDesignEvaluationRequestDataBrokerStub(gui_channel)
    # gui_result_stub = sudoku_gui_pb2_grpc.SudokuDesignEvaluationResultProcessorStub(gui_channel)
    gui_request_stub = orchestrator_pb2_grpc.SudokuDesignEvaluationRequestDataBrokerStub(gui_channel)
    gui_result_stub = orchestrator_pb2_grpc.SudokuDesignEvaluationResultProcessorStub(gui_channel)

    evaluator_channel = grpc.insecure_channel('localhost:'+str(config['designevaluator-grpcport']))
    # evaluator_program_encoder_stub = sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluationProblemEncoderStub(evaluator_channel)
    # evaluator_result_decoder_stub = sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluationResultDecoderStub(evaluator_channel)
    evaluator_program_encoder_stub = orchestrator_pb2_grpc.SudokuDesignEvaluationProblemEncoderStub(evaluator_channel)
    evaluator_result_decoder_stub = orchestrator_pb2_grpc.SudokuDesignEvaluationResultDecoderStub(evaluator_channel)

    aspsolver_channel = grpc.insecure_channel('localhost:'+str(config['aspsolver-grpcport']))
    # aspsolver_stub = asp_pb2_grpc.OneshotSolverStub(aspsolver_channel)
    aspsolver_stub = orchestrator_pb2_grpc.OneshotSolverStub(aspsolver_channel)

    while True:
      try:
        logging.info("calling SudokuDesignEvaluationRequestDataBroker.requestSudokuEvaluation() with empty dummy")
        #dummy1 = sudoku_gui_pb2.SudokuDesignEvaluationRequest()
        dummy1 = orchestrator_pb2.SudokuDesignEvaluationRequest()
        guijob = gui_request_stub.requestSudokuEvaluation(dummy1)

        logging.info("calling SudokuDesignEvaluationProblemEncoder.evaluateSudokuDesign() with payload %s", guijob)
        solverjob = evaluator_program_encoder_stub.evaluateSudokuDesign(guijob)

        logging.info("calling OneshotSolver.solve() with payload %s", solverjob)
        aspresult = aspsolver_stub.solve(solverjob)

        logging.info("calling SudokuDesignEvaluationResultDecoder.processEvaluationResult() with payload %s", aspresult)
        evalresult = evaluator_result_decoder_stub.processEvaluationResult(aspresult)

        logging.info("calling SudokuDesignEvaluationResultProcessor.processEvaluationResult() with payload %s", evalresult)
        dummy2 = gui_result_stub.processEvaluationResult(evalresult)

      except Exception:
        logging.error("exception (retrying after 2 seconds): %s", traceback.format_exc())
        # do not spam
        time.sleep(2)

main()