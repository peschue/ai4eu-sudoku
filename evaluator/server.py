import concurrent.futures
import grpc
import json
import logging
import os
import re
import sys
import time

import sudoku_design_evaluator_pb2
import sudoku_design_evaluator_pb2_grpc

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

class SudokuDesignEvaluatorServicerImpl(sudoku_design_evaluator_pb2_grpc.SudokuDesignEvaluatorServicer):
    def __init__(self):
        self.encoding = '''
            % Adapted from an example by Hakan Kjellerstrand, hakank@gmail.com
            % See also http://www.hakank.org/answer_set_programming/

            % input:
            % * a partially defined sudoku field
            %   x(Row,Col,Value)
            %
            % output:
            % * a (cardinality-)minimal set of input fields that needs to be omitted to make the sudoku satisfiable
            %   omit(Row,Col,Value)
            % * a fully defined sudoku field
            %   y(Row,Col,Value)
            
            %
            % domains
            %
            val(1..9).
            border(1;4;7).

            % guess omissions
            { omit(Row,Col,Value) } :- x(Row,Col,Value).

            % minimize omissions
            :~ omit(Row,Col,Value). [1@1,Row,Col,Value]

            % define resulting field
            y(Row,Col,Value) :- x(Row,Col,Value), not omit(Row,Col,Value).

            % alldifferent boxes
            1 { y(X,Y,N) : val(X), val(Y), 
                X1<=X, X<=X1+2, Y1<=Y, Y<=Y1+2 } 1 :- val(N), border(X1), border(Y1).

            % alldifferent rows, columns
            1 { y(X,Y,N) : val(X) } 1 :- val(N), val(Y).
            1 { y(X,Y,N) : val(Y) } 1 :- val(N), val(X).

            % guess values
            1 { y(X,Y,N) : val(N) } 1 :- val(X), val(Y).

            #show.
            #show omit/3.
            #show y/3.
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
        # the following is for seeing part of the set of facts for debugging, if required
        #logging.warning("evaluateSudokuDesign with filtered facts %s", [ f for f in facts if re.match(r'x\([12],[12],.\)', f) ])
        facts = '\n'.join(facts)

        ret = sudoku_design_evaluator_pb2.SolverJob()
        ret.parameters.number_of_answers = 2 # at least 2, but we can use higher numbers.
        ret.program = self.encoding + facts
        return ret

    def processSolverResult(self, request, context):
        answers = [
            {
                'y': [ a for a in ans.atoms if a.startswith('y') ],
                'omit': [ a for a in ans.atoms if a.startswith('omit') ]
            }
            for ans in request.answers
        ]
        logging.info("processSolverResult request with %s atoms in respective answer sets", [ { k : len(v) for k, v in answer.items() } for answer in answers ])
        #logging.warning("processSolverResult filtered atoms[0] %s", [ f for f in request.answers[0].atoms if re.match(r'y\([12],[12],.\)', f) ])

        ret = sudoku_design_evaluator_pb2.SudokuDesignEvaluationResult()

        if all([ len(a['omit']) == 0 for a in answers ]):
            if len(answers) == 1:
                # unique solution
                ret.status = 1
            else:
                # more than one solution
                ret.status = 2
        else:
            # no solution
            ret.status = 0

        if ret.status in [1,2]:
            # encode the consistent sudoku solutions
            # compute the intersection of all solutions
            
            # start with all at -1
            ret.solution.extend([ -1 for _ in range(0,81) ])

            # intersect with each answer
            for a in answers:
                for atm in a['y']:
                    # atm is of form x(x,y,val)
                    x, y, val = atm[2:-1].split(',')
                    x = int(x)-1
                    y = int(y)-1
                    val = int(val)
                    
                    # set -1 to value
                    # if value is already there and different -> set to 0
                    if ret.solution[x+y*9] == -1:
                        ret.solution[x+y*9] = val
                    elif ret.solution[x+y*9] != val:
                        ret.solution[x+y*9] = 0

            # set all -1 to 0
            for idx in range(0,81):
                if ret.solution[idx] == -1:
                    ret.solution[idx] = 0
        else:
            # mark inconsistent fields

            # start with all at 0
            ret.inconsistency_involved.extend([ 0 for _ in range(0,81) ])

            # union with each answer
            for a in answers:
                for atm in a['omit']:
                    # atm is of form omit(x,y,val)
                    x, y, val = atm[5:-1].split(',')
                    x = int(x)-1
                    y = int(y)-1
                    val = int(val)

                    # set field (does not matter if it was set multiple times)
                    ret.inconsistency_involved[x+y*9] = val

        count_nonzero = lambda x: len([y for y in x if y != 0])
        logging.info("returning status %d, solution with %d nonzeroelements and inconsistency_involved with %d nonzero elements", ret.status, count_nonzero(ret.solution), count_nonzero(ret.inconsistency_involved))
        return ret

configfile = os.environ['CONFIG'] if 'CONFIG' in os.environ else "config.json"
logging.info("loading config from %s", configfile)
config = json.load(open(configfile, 'rt'))
grpcserver = grpc.server(
    concurrent.futures.ThreadPoolExecutor(max_workers=10),
    options=(
        ('grpc.keepalive_time_ms', 10000), # send each 10 seconds
        ('grpc.keepalive_timeout_ms', 3000), # 3 second = timeout
        ('grpc.keepalive_permit_without_calls', True), # allow ping without RPC calls
        ('grpc.http2.max_pings_without_data', 0), # allow unlimited pings without data
        ('grpc.http2.min_time_between_pings_ms', 5000), # allow pings every 10 seconds
        ('grpc.http2.min_ping_interval_without_data_ms', 5000), # allow pings without data every 5 seconds
    )
)
sudoku_design_evaluator_pb2_grpc.add_SudokuDesignEvaluatorServicer_to_server(SudokuDesignEvaluatorServicerImpl(), grpcserver)
grpcport = config['grpcport']
# listen on all interfaces (otherwise docker cannot export)
grpcserver.add_insecure_port('0.0.0.0:'+str(grpcport))
logging.info("starting grpc server at port %d", grpcport)
grpcserver.start()

while True:
    time.sleep(1)
