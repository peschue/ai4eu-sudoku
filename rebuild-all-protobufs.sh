
# this script is only required for starting daemons locally without docker
# Dockerfile 

pushd gui
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. sudoku-gui.proto
popd

pushd aspsolver
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. asp.proto
popd

pushd evaluator
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. sudoku-design-evaluator.proto
popd

pushd orchestrator
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. orchestrator.proto
popd

