import os
import logging
import json
import time
import grpc
import concurrent.futures

import asp_pb2
import asp_pb2_grpc

# this is the ASP solver! (e.g., conda install clingo)
import clingo

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


class GRPCServicer(asp_pb2_grpc.OneShotAnswerSetSolverServicer):
    def __init__(self):
        pass

    def solve(self, request, context):
        logging.info("solve request: %s", request)

        c = clingo.Control([str(request.parameters.number_of_answers), '--opt-mode=optN'])
        c.add('base', [], request.program)
        c.ground([('base', [])])

        ret = asp_pb2.SolveResultAnswersets()
        logging.info("solving")
        for answer in c.solve(yield_=True):
            if answer.cost != [] and not answer.optimality_proven:
                logging.info("skipping non-optimality-proven answer with cost %s", answer.cost)
                continue

            logging.info("answer: %s", answer)
            ans = asp_pb2.Answerset()
            ans.atoms.extend([str(a) for a in answer.symbols(shown=True)])
            ans.costs.extend([asp_pb2.CostElement(level=level, cost=cost) for level, cost in enumerate(answer.cost)])
            ans.is_known_optimal = answer.optimality_proven
            ret.answers.append(ans)
        logging.info("finished: %d answers", len(ret.answers))
        return ret


configfile = os.environ['CONFIG'] if 'CONFIG' in os.environ else "config.json"
logging.info("loading config from %s", configfile)
config = json.load(open(configfile, 'rt'))
grpcserver = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
asp_pb2_grpc.add_OneShotAnswerSetSolverServicer_to_server(GRPCServicer(), grpcserver)
grpcport = config['grpcport']
# listen on all interfaces (otherwise docker cannot export)
grpcserver.add_insecure_port('0.0.0.0:' + str(grpcport))
logging.info("starting grpc server at port %d", grpcport)
grpcserver.start()

while True:
    time.sleep(1)
