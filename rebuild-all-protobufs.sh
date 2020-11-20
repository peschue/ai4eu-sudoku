
# this script is only required for starting daemons locally without docker
# Dockerfile 

pushd gui
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto
popd

pushd aspsolver
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto
popd

pushd evaluator
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto
popd

pushd orchestrator
python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto
popd

