# AI4EU Sudoku Hello World

PoC for a Sudoku design assistant based on ASP, gRPC, and Protobuf, deployable in AI4EU Experiments.

A Tutorial video about this "Sudoku Hello World" can be found here:
https://www.youtube.com/watch?v=gM-HRMNOi4w

# Prerequisites

You can run everything manually without docker, but docker is recommended for use with the helper script `helper.py`.

The easiest is to use conda and the script `./create-conda-environment.sh` which creates an environment called `ai4eusudoku` that contains all required prerequisites.

Without conda, all packages except `clingo` can be installed with `pip`. For `clingo` see the build instructions in `./aspsolver/Dockerfile`.

If you use conda (and generated the environment as indicated above) then, before doing anything mentioned below, you need to run `conda activate ai4eusudoku` in the shell where you run one of the scripts below.

# Running the whole pipeline locally in docker

The following commands build three docker images, run them, and then start an orchestrator outside of docker.

```
$ ./helper.py build-protobufs
$ ./helper.py build
$ ./helper.py run detached
$ ./helper.py orchestrate
```

You can see the running containers with the command

```
$ ./helper.py run detached
```

You should see a list of three containers, all in status "Up" with ports 8000-8003 exported.

In a new browser window open http://localhost:8000/ and you should see a Sudoku grid.

You can follow the logs of each docker container using `./helper.py follow <component>`, for example `./helper.py follow gui`.

# Running Sudoku using AI4EU Experiments Acumos

First we onboarding three components to AI4EU Experiments Acumos platform (Gui, Evaluator, ASP Solver).

These components are all built from this repository and first need to be uploaded to a docker registry.

## Pushing Images to a Container Registry

To build the docker images and upload them to the registry, the workflow is as follows.

* configure REMOTE_REPO in `./helper.py`.
* login to the remote repo with `docker login <your REMOTE_REPO>`

```
$ ./helper.py build
$ ./helper.py tag-and-push
```

## Docker Registries and Images

Decide on which docker registry you want to host the images. Setup the URI and port in variable `REMOTE_REPO`, e.g., `export REMOTE_REPO=cicd.ai4eu-dev.eu:7444`.
Log in to the registry with `docker login <URI>`.
Run `./helper.py tag-and-push`. If it fails, retrying can help. Maybe multiple times.

## Register components in AI4EU Experiments

Login to the platform and use "On-boarding Model" menu item and there "On-board dockerized Model URI".

You extract host and port from the `REMOTE_REPO` where you pushed your images (see above).

Images are tagged as

* `gui-<version>`
* `evaluator-<version>`
* `aspsolver-<version>`

Versions are defined in the top of `helper.py`.

The protobuf files to upload are in the component directories:

*  `gui/sudoku-gui.proto`
*  `evaluator/sudoku-desgin-evaluator.proto`
*  `aspsolver/asp.proto`

You do **not** need to upload `orchestrator/orchestrator.proto` anywhere because the generic orchestrator within AI4EU Experiments will automatically assemble a suitable protobuf file.

For example to onboard the ASP Solver:

* registry: cicd.ai4eu-dev.eu
* port: 7444
* image: tutorials/sudoku
* tag: aspsolver-1.1
* protobuf file (press upload!): aspsolver/asp.proto

Finally, once the model is "on-boarded" the category needs to be set in "My Models" -> select model -> "Manage Model" -> "Publish to Marketplace" -> "Model Category". (You can ignore error message about author name, you can choose "Data Transformer" and "Scikit-learn" for all models.)

## Assemble, Save, and Validate Solution

See the video.

## Download Solution Package

See the video.

## Deploy in a kubernetes environment

# Development Documentation

You can test each component (GUI, ASP Solver, Sudoku Evaluator) independent from other components.
This section shows how to run each component and test it.

## Individual start of each docker container and testing

First, build protobuf python files for testing and orchestration by running the following.

```
$ ./helper.py build-protobufs
```

* GUI

  In some terminal:

  ```
  $ ./helper.py build gui
  $ ./helper.py run interactive gui
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
  $ ./helper.py run interactive evaluator
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
  $ ./helper.py run interactive aspsolver
  ```

  In another terminal:

  ```
  $ cd aspsolver/
  $ ./test.py
  ```

  You should see in the first terminal that the request arrived and was handled.

## Protobuf Files

We have three protobuf files that contain redundant content (AI4EU Experiments Acumos currently does not support `import`).
These three files that can be hand-edited are:

  * `aspsolver/asp.proto`
  * `evaluator/sudoku-design-evaluator.proto`
  * `gui/sudoku-gui.proto`

The non-generic Orchestrator in `orchestrator/` uses a manually assembled protobuf file that contains the union of the above files with duplicates removed: `orchestrator/orchestrator.proto`. This file is not required for the AI4EU Experiments platform.

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
