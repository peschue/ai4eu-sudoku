#!/usr/bin/env python

#
# this script helps to build/deploy the sudoku acumos example
# it basically helps with docker commands and compiling protobuf
#

import subprocess
import sys
import logging

# we describe each image and which ports need to be redirected to which ports
# according to the container specification,
# the gRPC server must run at 8061 and the web gui (if exists) at 8062
METADATA = {
    'gui': {
        'version': '1.4',
        'ports': {8061: 8001, 8062: 8000},
    },
    'evaluator': {
        'version': '1.4',
        'ports': {8061: 8002},
    },
    'aspsolver': {
        'version': '1.1',
        'ports': {8061: 8003},
    }
}

REMOTE_REPO = 'cicd.ai4eu-dev.eu:7444/tutorials/sudoku'
# REMOTE_REPO = 'peterschueller/test'

COMPONENTS = ['gui', 'evaluator', 'aspsolver']

USAGE = '''
Helps to build/deploy the Sudoku Acumos example.

Usage for building and pushing to docker registry:
    {self} build-protobufs
    {self} build [component]
    {self} tag-and-push [component]

Usage for running locally using docker:
    {self} run {{detached|interactive|shell}} [component]
    {self} kill [component]
    {self} follow [component]
    {self} list
    {self} orchestrate

where [component] is one of {comps}
'''


def cmd_info(cmd, cwd=None):
    if cwd is None:
        sys.stderr.write("RUNNING %s\n" % cmd)
    else:
        sys.stderr.write("IN %s RUNNING %s\n" % (cwd, cmd))
    sys.stderr.flush()


class ShowUsage(Exception):
    pass


def build_protobufs():

    cmd = 'python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto'

    for component in COMPONENTS + ['orchestrator']:

        logging.info('running in %s', component)
        cmd_info(cmd, cwd=component)
        subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def build(component):

    logging.info("building component %s", component)

    cmd = "docker build -t ai4eu-sudoku:{}-{} .".format(
        component, METADATA[component]['version'])
    cmd_info(cmd, cwd=component)
    subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def tag_and_push(component):

    logging.info("tagging component %s", component)

    x = {
        'comp': component,
        'ver': METADATA[component]['version'],
        'repo': REMOTE_REPO
    }
    cmd = "docker tag ai4eu-sudoku:{comp}-{ver} {repo}:{comp}-{ver}".format(**x)
    cmd_info(cmd, cwd=component)
    subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)

    logging.info("pushing component %s", component)

    cmd = "docker push {repo}:{comp}-{ver}".format(**x)
    cmd_info(cmd, cwd=component)
    subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def run(mode, component):
    if mode not in ['detached', 'interactive', 'shell']:
        raise ShowUsage()

    x = {
        'comp': component,
        'ver': METADATA[component]['version'],
        'ports': ' '.join([
            '--publish={ext}:{int}'.format(int=int, ext=ext)
            for int, ext in METADATA[component]['ports'].items()
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
    cmd_info(cmd, cwd=component)
    subprocess.check_call(cmd, cwd=component, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def kill(component):

    cmd = "docker container ls -q --filter name=ai4eu-sudoku-{}".format(component)
    cmd_info(cmd)
    out = subprocess.check_output(cmd, shell=True)
    out = out.decode('utf8').strip()

    if out == '':
        logging.warning("nothing to kill for %s", component)
        return

    logging.info("got container %s for component %s", out, component)
    cmd = "docker container kill {}".format(out)
    cmd_info(cmd)
    subprocess.call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

    logging.info("removing container %s", component)
    cmd = "docker container rm ai4eu-sudoku-{}".format(component)
    cmd_info(cmd)
    # ignore failure!
    subprocess.call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def follow(component):

    cmd = "docker logs -f ai4eu-sudoku-{}".format(component)
    cmd_info(cmd)
    subprocess.call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)


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

        elif mode == 'follow':

            if len(args) == 1 and args[0] in COMPONENTS:
                follow(args[0])
            else:
                raise ShowUsage()

        elif mode == 'list':

            subprocess.check_call('docker container list --all --filter name=ai4eu-sudoku*', shell=True, stdout=sys.stdout, stderr=sys.stderr)

        elif mode == 'orchestrate':

            cmd = 'python orchestrator.py'
            cwd = 'orchestrator'
            cmd_info(cmd, cwd=cwd)
            subprocess.check_call(cmd, cwd=cwd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

    except ShowUsage:
        logging.error(USAGE.format(
            self=sys.argv[0],
            comps=' '.join(COMPONENTS)
        ))
        return -1


if __name__ == '__main__':
    main()
