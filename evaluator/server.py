import os
import logging
import json
import time
import grpc
import concurrent.futures
import sys

sys.path.append('../protobuf/')
import sudoku_design_evaluator_pb2_grpc
import sudoku_design_evaluator_pb2

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

class GRPCSudokuDesignEvaluationProblemEncoderServicer(sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluationProblemEncoderServicer):
    def __init__(self):
        pass

    def evaluateSudokuDesign(self, request, context):
        logging.info("evaluateSudokuDesign request: %s", request)

        ret = sudoku_design_evaluator_pb2.SolverJob()
        return ret

class GRPCSudokuDesignEvaluationResultDecoderServicer(sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluationResultDecoderServicer):
    def __init__(self):
        pass

    def processEvaluationResult(self, request, context):
        logging.info("processEvaluationResult request: %s", request)

        ret = sudoku_design_evaluator_pb2.SudokuDesignEvaluationResult()
        return ret

configfile = os.environ['CONFIG'] if 'CONFIG' in os.environ else "../config.json"
logging.info("loading config from %s", configfile)
config = json.load(open(configfile, 'rt'))
grpcserver = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
sudoku_design_evaluator_pb2_grpc.add_SudokuDesignEvaluationProblemEncoderServicer_to_server(GRPCSudokuDesignEvaluationProblemEncoderServicer(), grpcserver)
sudoku_design_evaluator_pb2_grpc.add_SudokuDesignEvaluationResultDecoderServicer_to_server(GRPCSudokuDesignEvaluationResultDecoderServicer(), grpcserver)
grpcport = config['designevaluator-grpcport']
grpcserver.add_insecure_port('localhost:'+str(grpcport))
logging.info("starting grpc server at port %d", grpcport)
grpcserver.start()

while True:
    time.sleep(1)