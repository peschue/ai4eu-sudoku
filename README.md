# ai4eu-sudoku

PoC for a Sudoku design assistant based on ASP, gRPC, and Protobuf, deployable in AI4EU Experiments.

# Prerequisites

The easiest is to use conda and the script `./create-conda-environment.sh` which creates an environment called `ai4eusudoku` that contains all required prerequisites.

Without conda, all packages except `clingo` can be installed with `pip`. For `clingo` see the build instructions in `./aspsolver/Dockerfile`.

# Starting and Testing

If you just cloned the repo or checked out a new version or edited any `.proto` file:

* run `./populate-duplicate-protobufs.sh`
* run `./rebuild-all-protobufs.sh`

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
  $ cd gui/
  $ ./docker-build.sh
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
  $ cd evaluator/
  $ ./docker-build.sh
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
  $ cd aspsolver/
  $ ./docker-build.sh
  $ ./docker-run-interactive.sh
  ```

  In another terminal:

  ```
  $ cd aspsolver/
  $ ./test.py
  ```

  You should see in the first terminal that the request arrived and was handled.

# Running the whole pipeline

```
$ ./populate-duplicate-protobufs.sh
$ ./docker-build-all.sh
$ ./docker-run-all-detached.sh
$ ./docker-list-containers.sh
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

# Protobuf Issues

We have 4 protobuf files.

3 protobuf files for components.
1 protobuf file for the orchestrator.

We only need the orchestrator protobuf file, because otherwise we will get name clashes because certain classes are defined in multiple compilation units.
The orchestrator file contains all definitions of all components, but each definition only once.

# Representation

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
