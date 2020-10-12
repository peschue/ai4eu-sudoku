import os
import logging
import json
import time
import grpc
import concurrent.futures
import sys

sys.path.append('../protobuf/')
import asp_pb2_grpc
import asp_pb2

# this is the ASP solver! (e.g., conda install clingo)
import clingo

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

class GRPCOneshotSolverServicer(asp_pb2_grpc.OneshotSolverServicer):
    def __init__(self):
        pass

    def solve(self, request, context):
        logging.info("solve request: %s", request)

        c = clingo.Control([ str(request.parameters.number_of_answers) ])
        c.add('base', [], request.program)
        c.ground([('base',[])])

        ret = asp_pb2.SolveResultAnswersets()
        logging.info("solving")
        for answer in c.solve(yield_=True):
            logging.info("answer: %s", answer)
            ans = asp_pb2.Answerset()
            ans.atoms.extend([ str(a) for a in answer.symbols(atoms=True) ])
            ret.answers.append(ans)
        return ret

configfile = os.environ['CONFIG'] if 'CONFIG' in os.environ else "../config.json"
logging.info("loading config from %s", configfile)
config = json.load(open(configfile, 'rt'))
grpcserver = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
asp_pb2_grpc.add_OneshotSolverServicer_to_server(GRPCOneshotSolverServicer(), grpcserver)
grpcport = config['aspsolver-grpcport']
grpcserver.add_insecure_port('localhost:'+str(grpcport))
logging.info("starting grpc server at port %d", grpcport)
grpcserver.start()

while True:
    time.sleep(1)