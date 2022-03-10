# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import auth_service_pb2 as auth__service__pb2


class AuthServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RegisterUser = channel.unary_unary(
                '/auth_service.AuthService/RegisterUser',
                request_serializer=auth__service__pb2.RegisterUserInput.SerializeToString,
                response_deserializer=auth__service__pb2.UserLoginResponse.FromString,
                )
        self.LoginUser = channel.unary_unary(
                '/auth_service.AuthService/LoginUser',
                request_serializer=auth__service__pb2.UserLoginWithPassword.SerializeToString,
                response_deserializer=auth__service__pb2.UserLoginResponse.FromString,
                )
        self.GenerateMobileOTP = channel.unary_unary(
                '/auth_service.AuthService/GenerateMobileOTP',
                request_serializer=auth__service__pb2.MobileInput.SerializeToString,
                response_deserializer=auth__service__pb2.BooleanResponse.FromString,
                )
        self.ValidateMobileOTP = channel.unary_unary(
                '/auth_service.AuthService/ValidateMobileOTP',
                request_serializer=auth__service__pb2.ValidateMobileOTPInput.SerializeToString,
                response_deserializer=auth__service__pb2.BooleanResponse.FromString,
                )
        self.GetUserList = channel.unary_unary(
                '/auth_service.AuthService/GetUserList',
                request_serializer=auth__service__pb2.Empty.SerializeToString,
                response_deserializer=auth__service__pb2.UserListResponse.FromString,
                )


class AuthServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RegisterUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LoginUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GenerateMobileOTP(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ValidateMobileOTP(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUserList(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AuthServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RegisterUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterUser,
                    request_deserializer=auth__service__pb2.RegisterUserInput.FromString,
                    response_serializer=auth__service__pb2.UserLoginResponse.SerializeToString,
            ),
            'LoginUser': grpc.unary_unary_rpc_method_handler(
                    servicer.LoginUser,
                    request_deserializer=auth__service__pb2.UserLoginWithPassword.FromString,
                    response_serializer=auth__service__pb2.UserLoginResponse.SerializeToString,
            ),
            'GenerateMobileOTP': grpc.unary_unary_rpc_method_handler(
                    servicer.GenerateMobileOTP,
                    request_deserializer=auth__service__pb2.MobileInput.FromString,
                    response_serializer=auth__service__pb2.BooleanResponse.SerializeToString,
            ),
            'ValidateMobileOTP': grpc.unary_unary_rpc_method_handler(
                    servicer.ValidateMobileOTP,
                    request_deserializer=auth__service__pb2.ValidateMobileOTPInput.FromString,
                    response_serializer=auth__service__pb2.BooleanResponse.SerializeToString,
            ),
            'GetUserList': grpc.unary_unary_rpc_method_handler(
                    servicer.GetUserList,
                    request_deserializer=auth__service__pb2.Empty.FromString,
                    response_serializer=auth__service__pb2.UserListResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'auth_service.AuthService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class AuthService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RegisterUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/auth_service.AuthService/RegisterUser',
            auth__service__pb2.RegisterUserInput.SerializeToString,
            auth__service__pb2.UserLoginResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def LoginUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/auth_service.AuthService/LoginUser',
            auth__service__pb2.UserLoginWithPassword.SerializeToString,
            auth__service__pb2.UserLoginResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GenerateMobileOTP(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/auth_service.AuthService/GenerateMobileOTP',
            auth__service__pb2.MobileInput.SerializeToString,
            auth__service__pb2.BooleanResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ValidateMobileOTP(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/auth_service.AuthService/ValidateMobileOTP',
            auth__service__pb2.ValidateMobileOTPInput.SerializeToString,
            auth__service__pb2.BooleanResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetUserList(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/auth_service.AuthService/GetUserList',
            auth__service__pb2.Empty.SerializeToString,
            auth__service__pb2.UserListResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
