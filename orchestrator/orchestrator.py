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

import othread

# generated from .proto
import orchestrator_pb2 as pb
import orchestrator_pb2_grpc as pb_grpc


logging.basicConfig(level=logging.DEBUG)


configfile = "config.json"
config = json.load(open(configfile, 'rt'))


def main():
    om = othread.OrchestrationManager()

    gui_request_thread = om.create_thread(
        stream_in=False, stream_out=True, empty_in=True,
        host='localhost', port=config['gui-grpcport'],
        service='SudokuGUI', rpc='requestSudokuEvaluation')
    # TODO add inputmessage / outputmessage (json representation?)
    gui_result_thread = om.create_thread(
        stream_in=True, stream_out=False, empty_out=True,
        host='localhost', port=config['gui-grpcport'],
        service='SudokuGUI', rpc='processEvaluationResult')
    eval_evaluate_thread = om.create_thread(
        stream_in=False, stream_out=False,
        host='localhost', port=config['designevaluator-grpcport'],
        service='SudokuDesignEvaluator', rpc='evaluateSudokuDesign')
    eval_process_thread = om.create_thread(
        stream_in=False, stream_out=False,
        host='localhost', port=config['designevaluator-grpcport'],
        service='SudokuDesignEvaluator', rpc='processSolverResult')
    asp_thread = om.create_thread(
        stream_in=False, stream_out=False,
        host='localhost', port=config['aspsolver-grpcport'],
        service='OneShotAnswerSetSolver', rpc='solve')

    eval_job_queue = om.create_queue(name='eval_job', message='SudokuDesignEvaluationJob')
    eval_result_queue = om.create_queue(name='eval_result', message='SudokuDesignEvaluationResult')
    asp_job_queue = om.create_queue(name='asp_job', message='SolverJob')
    answersets_queue = om.create_queue(name='answersets', message='SolveResultAnswersets')

    gui_request_thread.attach_output_queue(eval_job_queue)
    eval_evaluate_thread.attach_input_queue(eval_job_queue)

    eval_evaluate_thread.attach_output_queue(asp_job_queue)
    asp_thread.attach_input_queue(asp_job_queue)

    asp_thread.attach_output_queue(answersets_queue)
    eval_process_thread.attach_input_queue(answersets_queue)

    eval_process_thread.attach_output_queue(eval_result_queue)
    gui_result_thread.attach_input_queue(eval_result_queue)

    om.orchestrate_forever()


main()
