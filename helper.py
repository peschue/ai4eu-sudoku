#!/usr/bin/env python

#
# this script helps to build/deploy the sudoku acumos example
# it basically helps with docker commands and compiling protobuf
#

import subprocess
import sys
import logging

METADATA = {
    'gui': {
        'version': '1.3',
        'ports': [8000, 8001],
    },
    'evaluator': {
        'version': '1.3',
        'ports': [8002],
    },
    'aspsolver': {
        'version': '1.0',
        'ports': [8003],
    }
}

REMOTE_REPO = 'cicd.ai4eu-dev.eu:7444/tutorials/sudoku'
# REMOTE_REPO = 'peterschueller/test'

COMPONENTS = ['gui', 'evaluator', 'aspsolver']

USAGE = '''
Helps to build/deploy the Sudoku Acumos example.

Usage:
    {self} populate-protobufs
    {self} build-protobufs

    {self} build [component]
    {self} tag-and-push [component]

    {self} run {{detached|interactive|shell}} [component]
    {self} kill [component]
    {self} list

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
        subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def build_protobufs():

    cmd = 'python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto'
    logging.info(cmd)

    for component in COMPONENTS + ['orchestrator']:

        logging.info('running in %s', component)
        subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)


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


def run(mode, component):
    if mode not in ['detached', 'interactive', 'shell']:
        raise ShowUsage()

    x = {
        'comp': component,
        'ver': METADATA[component]['version'],
        'ports': ' '.join([
            '--publish={p}:{p}'.format(p=port)
            for port in METADATA[component]['ports']
        ]),
        'repo': REMOTE_REPO,
        'args': '--rm',  # remove image after run
        'cmd': ''
    }

    if mode == 'interactive':
        x['args'] += ' -it'
    elif mode == 'detached':
        x['args'] += ' -d'
    elif mode == 'shell':
        x['args'] += ' -it'
        x['cmd'] = '/bin/bash'

    cmd = 'docker run {args} --name ai4eu-sudoku-{comp} {ports} ai4eu-sudoku:{comp}-{ver} {cmd}'.format(**x)
    subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def kill(component):

    cmd = "docker container ls -q --filter name=ai4eu-sudoku-{}".format(component)
    out = subprocess.check_output(cmd, shell=True)
    out = out.decode('utf8').strip()

    if out == '':
        logging.warning("nothing to kill for %s", component)
        return

    logging.info("got container %s for component %s", out, component)
    cmd = "docker container kill {}".format(out)
    subprocess.call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

    logging.info("removing container %s", component)
    cmd = "docker container rm ai4eu-sudoku-{}".format(component)
    subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)


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

        elif mode == 'build-protobufs':

            if args != []:
                raise ShowUsage()
            build_protobufs()

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

        elif mode == 'run':

            if len(args) == 1:
                mode = args[0]
                for c in COMPONENTS:
                    run(args[0], c)
            elif len(args) == 2 and args[1] in COMPONENTS:
                run(args[0], args[1])
            else:
                raise ShowUsage()

        elif mode == 'kill':

            if len(args) == 0:
                for c in COMPONENTS:
                    kill(c)
            elif args[0] in COMPONENTS:
                kill(args[0])
            else:
                raise ShowUsage()

        elif mode == 'list':

            subprocess.check_call('docker container list --all --filter name=ai4eu-sudoku*', shell=True, stdout=sys.stdout, stderr=sys.stderr)

    except ShowUsage:
        logging.error(USAGE.format(
            self=sys.argv[0],
            comps=' '.join(COMPONENTS)
        ))
        return -1


if __name__ == '__main__':
    main()
