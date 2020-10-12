# build protobuf python sources

python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. sudoku-gui.proto
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. asp.proto
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. sudoku-design-evaluator.proto

