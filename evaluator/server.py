import concurrent.futures
import grpc
import json
import logging
import os
import re
import sys
import time

sys.path.append('../protobuf/')
import sudoku_design_evaluator_pb2_grpc
import sudoku_design_evaluator_pb2

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

class GRPCSudokuDesignEvaluationProblemEncoderServicer(sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluationProblemEncoderServicer):
    def __init__(self):
        self.encoding = '''
            % Adapted from an example by Hakan Kjellerstrand, hakank@gmail.com
            % See also http://www.hakank.org/answer_set_programming/

            % x(Row,Col,Value).

            %
            % domains
            %
            val(1..9).
            border(1;4;7).

            % alldifferent boxes
            1 { x(X,Y,N) : val(X), val(Y), 
                X1<=X, X<=X1+2, Y1<=Y, Y<=Y1+2 } 1 :- val(N), border(X1), border(Y1).

            % alldifferent rows, columns
            1 { x(X,Y,N) : val(X) } 1 :- val(N), val(Y).
            1 { x(X,Y,N) : val(Y) } 1 :- val(N), val(X).

            % guess values
            1 { x(X,Y,N) : val(N) } 1 :- val(X), val(Y).

            #show.
            #show x/3.
        '''

    def evaluateSudokuDesign(self, request, context):
        logging.info("evaluateSudokuDesign request with field of size %d", len(request.field))

        # we got the partial sudoku field
        # we encode it as x(Row,Col,Value) and add the encoding
        facts = [
            'x({},{},{}).'.format(x+1,y+1,request.field[x+9*y])
            for x in range(0,9)
            for y in range(0,9)
            if request.field[x+9*y] > 0
        ]
        logging.warning("evaluateSudokuDesign with filtered facts %s", [ f for f in facts if re.match(r'x\([12],[12],.\)', f) ])
        facts = '\n'.join(facts)

        ret = sudoku_design_evaluator_pb2.SolverJob()
        ret.parameters.number_of_answers = 2
        ret.program = self.encoding + facts
        return ret

class GRPCSudokuDesignEvaluationResultDecoderServicer(sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluationResultDecoderServicer):
    def __init__(self):
        pass

    def processEvaluationResult(self, request, context):
        logging.info("processEvaluationResult request with %s atoms in respective answer sets", [ len(ans.atoms) for ans in request.answers ])

        ret = sudoku_design_evaluator_pb2.SudokuDesignEvaluationResult()
        ret.status = len(request.answers)

        if ret.status in [1,2]:
            # encode the single answer set
            ret.solution.extend([ 0 for _ in range(0,81) ])
            for atm in list(set(request.answers[0].atoms) & set(request.answers[1].atoms)):
                # atm is of form x(x,y,val)
                x, y, val = atm[2:-1].split(',')
                x = int(x)-1
                y = int(y)-1
                val = int(val)
                ret.solution[x+y*9] = val

            logging.warning("processEvaluationResult filtered atoms[0] %s", [ f for f in request.answers[0].atoms if re.match(r'x\([12],[12],.\)', f) ])


        logging.info("returning status %d and solution with %d elements", ret.status, len(ret.solution))
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