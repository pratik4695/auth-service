#!/usr/bin/env bash
#cd api-protos;
#echo 'Fetching latest protobufs from remote.'
#git pull origin develop;
#cd ..;
echo 'Invoking Protocol Compiler to generate classes.'
python -m grpc_tools.protoc -I ./api-protos --python_out=./ --grpc_python_out=./ ./api-protos/auth_service.proto;
