#!/usr/bin/env python3

import logging
import grpc
import sys
import json

import asp_pb2_grpc
import asp_pb2

configfile = "config.json"
config = json.load(open(configfile, 'rt'))

logging.basicConfig(level=logging.DEBUG)

def main():
   channel = grpc.insecure_channel('127.0.0.1:'+str(config['grpcport']))
   stub = asp_pb2_grpc.OneshotSolverStub(channel)

   job = asp_pb2.SolverJob()
   job.program = 'a :- not b. b :- not a. { c ; d ; e }. :~ a. [1,a] :~ c. [1,c]'
   job.parameters.number_of_answers = 5

   response = stub.solve(job)

   logging.info("got response '%s' (expect 4 optimal answers: {b}, {b,e}, {b,d}, {b,d,e})", response)

main()
