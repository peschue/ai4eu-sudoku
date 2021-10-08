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

import logging
import json
import time
import grpc
import traceback

# generated from .proto
import orchestrator_pb2 as pb
import orchestrator_pb2_grpc as pb_grpc


logging.basicConfig(level=logging.DEBUG)


configfile = "config.json"
config = json.load(open(configfile, 'rt'))


def main():
    guiconn = 'localhost:' + str(config['gui-grpcport'])
    evalconn = 'localhost:' + str(config['designevaluator-grpcport'])
    aspconn = 'localhost:' + str(config['aspsolver-grpcport'])

    logging.info("connecting to GUI at %s", guiconn)
    gui_channel = grpc.insecure_channel(guiconn)
    gui_stub = pb_grpc.SudokuGUIStub(gui_channel)

    logging.info("connecting to design evaluator at %s", evalconn)
    evaluator_channel = grpc.insecure_channel(evalconn)
    evaluator_stub = pb_grpc.SudokuDesignEvaluatorStub(evaluator_channel)

    logging.info("connecting to ASP solver at %s", aspconn)
    aspsolver_channel = grpc.insecure_channel(aspconn)
    aspsolver_stub = pb_grpc.OneShotAnswerSetSolverStub(aspsolver_channel)

    while True:
        try:
            logging.info("calling SudokuGUI.requestSudokuEvaluation() with empty dummy")
            dummy1 = pb.Empty()
            guijob = gui_stub.requestSudokuEvaluation(dummy1)

            logging.info("calling SudokuDesignEvaluator.evaluateSudokuDesign() with guijob")
            solverjob = evaluator_stub.evaluateSudokuDesign(guijob)

            logging.info("calling OneShotAnswerSetSolverStub.solve() with parameters %s", solverjob.parameters)
            aspresult = aspsolver_stub.solve(solverjob)

            logging.info(
                "calling SudokuDesignEvaluator.processEvaluationResult() with %d answer sets and description %s",
                len(aspresult.answers), aspresult.description)
            evalresult = evaluator_stub.processSolverResult(aspresult)

            logging.info(
                "calling SudokuGUI.processEvaluationResult() with status %d, len(solution)=%d, len(minimal_unsolvable)=%s",
                evalresult.status, len(evalresult.solution), len(evalresult.inconsistency_involved))
            _ = gui_stub.processEvaluationResult(evalresult)

        except Exception:
            logging.error("exception (retrying after 2 seconds): %s", traceback.format_exc())
            # do not spam
            time.sleep(2)


main()
