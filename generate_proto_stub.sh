#!/usr/bin/env bash
#cd api-protos;
#echo 'Fetching latest protobufs from remote.'
#git pull origin develop;
#cd ..;
echo 'Invoking Protocol Compiler to generate classes.'
python -m grpc_tools.protoc -I ./all_protos --python_out=./ --grpc_python_out=./ ./all_protos/auth_service.proto;
