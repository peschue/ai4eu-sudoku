#!/usr/bin/env python

#
# this script helps to build/deploy the sudoku acumos example
# it basically helps with docker commands and compiling protobuf
#

import subprocess
import sys
import os
import logging

METADATA = {
    'gui': {
        'version': '1.3',
    },
    'evaluator': {
        'version': '1.3',
    },
    'aspsolver': {
        'version': '1.0',
    }
}

# REMOTE_REPO = 'cidc.ai4eu-dev.eu:7444'
REMOTE_REPO = 'peterschueller/test'
# REMOTE_REPO = 'peterschueller/ai4eu-sudoku'

COMPONENTS = ['gui', 'evaluator', 'aspsolver']

USAGE = '''
Helps to build/deploy the Sudoku Acumos example.

Usage:
    {self} populate-protobufs
    {self} build [component]
    {self} tag-and-push [component]

where [component] is one of {comps}
'''


class ShowUsage(Exception):
    pass


def populate_protobufs():

    # This script is required because docker does not permit to follow symlinks to parent directories.
    # Therefore we have to copy and cannot symlink .proto files.
    for cmd in [
        'cp aspsolver/asp.proto evaluator/',
        'cp aspsolver/asp.proto gui/',
        'cp aspsolver/asp.proto orchestrator/',
        'cp evaluator/sudoku-design-evaluator.proto gui/',
        'cp evaluator/sudoku-design-evaluator.proto orchestrator/',
        'cp gui/sudoku-gui.proto orchestrator/',
    ]:

        logging.info(cmd)
        subprocess.check_call(cmd, shell=True)


def build(component):

    logging.info("building component %s", component)

    cmd = "docker build -t ai4eu-sudoku:{}-{} .".format(
        component, METADATA[component]['version'])
    subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def tag_and_push(component):

    logging.info("tagging component %s", component)

    x = {
        'comp': component,
        'ver': METADATA[component]['version'],
        'repo': REMOTE_REPO
    }
    cmd = "docker tag ai4eu-sudoku:{comp}-{ver} {repo}:{comp}-{ver}".format(**x)
    subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)

    logging.info("pushing component %s", component)

    cmd = "docker push {repo}:{comp}-{ver}".format(**x)
    subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def main():
    logging.basicConfig(level=logging.INFO)
    try:
        if len(sys.argv) == 1:
            raise ShowUsage()

        mode = sys.argv[1]
        args = sys.argv[2:]

        if mode == 'populate-protobufs':

            if args != []:
                raise ShowUsage()
            populate_protobufs()

        elif mode == 'build':

            if len(args) == 0:
                for c in COMPONENTS:
                    build(c)
            elif args[0] in COMPONENTS:
                build(args[0])
            else:
                raise ShowUsage()

        elif mode == 'tag-and-push':

            if len(args) == 0:
                for c in COMPONENTS:
                    tag_and_push(c)
            elif args[0] in COMPONENTS:
                tag_and_push(args[0])
            else:
                raise ShowUsage()

    except ShowUsage:
        logging.error(USAGE.format(
            self=sys.argv[0],
            comps=' '.join(COMPONENTS)
        ))
        return -1


if __name__ == '__main__':
    main()
