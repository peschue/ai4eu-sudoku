# ai4eu-sudoku

PoC for a Sudoku design assistant based on ASP, gRPC, and Protobuf, deployable in AI4EU Experiments.

# Prerequisites

The easiest is to use conda and the script `./create-conda-environment.sh` which creates an environment called `ai4eusudoku` that contains all required prerequisites.

Without conda, all packages except `clingo` can be installed with `pip`. For `clingo` see the build instructions in `./aspsolver/Dockerfile`.

If you use conda (and generated the environment as indicated above) then, before doing anything mentioned below, you need to run `conda activate ai4eusudoku` in the shell where you run one of the scripts below.

# Starting and Testing

If you just cloned the repo or checked out a new version or edited any `.proto` file:

* run `./helper.py populate-protobufs`
* run `./helper.py build-protobufs`

You can test each component (GUI, ASP Solver, Sudoku Evaluator) independent from other components.
This section shows how to run each component and test it.
The next section describes how to run the whole pipeline using an orchestrator.

## Running and Testing without docker

The whole pipeline can run without docker.
But you need to install all required packages.

* See Section Prerequisites, `conda` might be your friend.
* See Section Starting and Testing.
* Each component has a `run-<component>.sh` script that needs to be run in the respective directory.
* Components must be started before the orchestrator is started, but the order of components does not matter.
* You will end up with 4 terminals (3 components + orchestrator).

Then, in a new browser window open http://localhost:8000/ and click on the Sudoku Grid and observe the messages in the top window.

## Individual start of each docker container and testing

* GUI

  In some terminal:

  ```
  $ ./helper.py build gui
  $ ./docker-run-interactive.sh
  ```

  In a new browser window open http://localhost:8000/

  You should see a Sudoku grid and some requests in the terminal.

  In another terminal:

  ```
  $ cd gui/
  $ ./test.py
  ```

  The Sudoku grid in the browser should show "Click on a cell to change. Sudoku has a unique solution" and there should be a digit in each cell of the grid next to the question mark symbols.

* Sudoku Evaluator

  In some terminal:

  ```
  $ ./helper.py build evaluator
  $ ./docker-run-interactive.sh
  ```

  In another terminal:

  ```
  $ cd evaluator/
  $ ./test.py
  ```

  You should see in the first terminal that the request arrived and was handled.
  You should see an ASP Program in the response in the second terminal.

* ASP Solver

  In some terminal:

  ```
  $ ./helper.py build aspsolver
  $ ./docker-run-interactive.sh
  ```

  In another terminal:

  ```
  $ cd aspsolver/
  $ ./test.py
  ```

  You should see in the first terminal that the request arrived and was handled.

# Running the whole pipeline

In the following, the first script is included in this shell, the others are executed in a subshell!

```
$ ./helper.py populate-protobufs
$ ./helper.py build
$ ./helper.py run detached
$ ./helper.py list
```

You should see a list of three containers, all in status "Up" with ports 8000-8003 exported.

In a new browser window open http://localhost:8000/ and you should see a Sudoku grid.

To run the orchestrator:

```
$ cd orchestrator
$ python3 orchestrator.py
```

You should see a request. Changing fields in the GUI should create requests in the orchestrator and in the docker containers.

You can see a `tail -f` to a docker container log with `docker logs <containerid> -f` where `<containerid>` is the hash from `./docker-list-containers.sh`.

# Running Sudoku using Acumos

First we onboarding three components to Acumos (Gui, Evaluator, ASP Solver).

These components are all built from this repository and first need to be uploaded to a docker registry.

## Pushing Images to a Container Registry

To build the docker images and upload them to the registry, the workflow is as follows.

* configure REMOTE_REPO in `./helper.py`.
* login to the remote repo with `docker login <your REMOTE_REPO>`
* run the following - the missing `/` in the first line is intentional!

```
$ ./helper.py populate-protobufs
$ ./helper.py build
$ ./helper.py tag-and-push
```

## Docker Registries and Images

Decide on which docker registry you want to host the images. Setup the URI and port in variable `REMOTE_REPO`, e.g., `export REMOTE_REPO=cicd.ai4eu-dev.eu:7444`.
Log in to the registry with `docker login <URI>`.
Run `./helper.py tag-and-push`. If it fails, retrying can help. Maybe multiple times.

## Register components in Acumos

Login to Acumos and use "On-boarding Model" menu item and there "On-board dockerized Model URI".

You extract host and port from the `REMOTE_REPO` where you pushed your images (see above).

Images are tagged as

* `gui-<version>`
* `evaluator-<version>`
* `aspsolver-<version>`

Versions are defined in the top of `helper.py`.

The protobuf files to upload are in directory `acumos/`.

For example to onboard the ASP Solver:

* registry: cicd.ai4eu-dev.eu
* port: 7444
* image: sudoku/ai4eu
* tag: aspsolver-1.0
* protobuf file (press upload!): acumos/asp.proto

Finally, once the model is "on-boarded" the category needs to be set in "My Models" -> select model -> "Manage Model" -> "Publish to Marketplace" -> "Model Category". (You can ignore error message about author name, you can choose "Data Transformer" and "Scikit-learn" for all models.)

## Assemble, Save, and Validate Solution

See the video.

## Download Solution Package

See the video.

## Deploy in a kubernetes environment

# Development Documentation

## Protobuf Files

We have 6 protobuf files.

* 3 protobuf files used within components, they use `import` statement to avoid code duplication.

  The script `./helper.py populate-protobufs` manages these files, they must be copied to ecah subdirectory where they are used because of safety restrictions of docker.

  The files that you should hand-edit are:

  * `aspsolver/asp.proto`
  * `evaluator/sudoku-design-evaluator.proto`
  * `gui/sudoku-gui.proto`

* 3 protobuf files to be uploaded to Acumos (it currently does not support `import`).

  They are in directory `acumos/`.

WP3 is working on improving this situation so that only one version of each protobuf file is required.

## Representation

The Sudoku field is represented as follows:

* in Protobuf: as a `repeated int32 field`

  where addressing into the one-dimensional array is as follows: `field[(column-1)+9*(row-1)]` is the value representing the cell in column `column` and row `row` if we use 1-based counting (as usual in Sudoku).

  Examples:
  
  - The top left field is in row/column = 1/1 therefore it is represented by `field[0+9*0] = field[0]`.
  - The top right field is in row/column = 1/9 therefore it is represented by `field[0+9*8] = field[72]`.
  - The bottom left field is in row/column = 9/1 therefore it is represented by `field[8+9*0] = field[8]`.

* in HTML/DOM: as an `id` attribute of a `div` with class `cell` and value `column_row` with 1-based counting.

  Examples:

  - The top left field is in row/column = 1/1 therefore it is represented by `<div class="cell" id="1_1">...`.
  - The top right field is in row/column = 1/9 therefore it is represented by `<div class="cell" id="1_9">...`.
  - The bottom left field is in row/column = 9/1 therefore it is represented by `<div class="cell" id="9_1">...`.

* in ASP: as predicates `x(column,row,value)` for 1-based `columns`, `rows`, and digits `value`

  Examples:

  - The top left field is in row/column = 1/1 therefore it is represented by `x(1,1,V)` for some V in {1,...,9}.
  - The top right field is in row/column = 1/9 therefore it is represented by `x(9,1,V)`.
  - The bottom left field is in row/column = 9/1 therefore it is represented by `x(1,9,V)`.

* in REST: the Javascript GUI calls REST endpoint `/user_setcell?x=column&y=row&value=V` for 1-based values of `row`, `column`, and `V`.
