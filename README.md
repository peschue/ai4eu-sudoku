# ai4eu-sudoku

PoC for a Sudoku design assistant based on ASP, gRPC, and Protobuf, deployable in AI4EU Experiments.

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
