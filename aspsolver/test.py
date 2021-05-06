#!/usr/bin/env python3

import logging
import grpc
import json

import asp_pb2_grpc
import asp_pb2

configfile = "config.json"
config = json.load(open(configfile, 'rt'))

logging.basicConfig(level=logging.DEBUG)


def main():
    # !!! here it is hardcoded to use the external port that ./helper.py assigns to the docker container !!!
    # !!! if you run without docker, you need to use port 8061 !!!
    channel = grpc.insecure_channel('localhost:8003')
    stub = asp_pb2_grpc.OneShotAnswerSetSolverStub(channel)

    job = asp_pb2.SolverJob()
    job.program = 'a :- not b. b :- not a. { c ; d ; e }. :~ a. [1,a] :~ c. [1,c]'
    job.parameters.number_of_answers = 5

    response = stub.solve(job)

    logging.info("got response '%s' (expect 4 optimal answers: {b}, {b,e}, {b,d}, {b,d,e})", response)


main()
