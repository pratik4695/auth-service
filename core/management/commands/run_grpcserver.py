import time
from concurrent import futures
from contextlib import contextmanager

import grpc
from django.core.management import BaseCommand

from User.grpcs import RegisterUser, LoginUser, GenerateMobileOTP, ValidateMobileOTP, GetUserList, EditUserDetail, \
    AuthenticateUserViaJWT
from User.grpcs.user import GetUserIDsDetail
from auth_service_pb2_grpc import AuthServiceServicer, add_AuthServiceServicer_to_server


class AuthService(AuthServiceServicer):
    def RegisterUser(self, request, context):
        return RegisterUser(request, context).__call__()

    def LoginUser(self, request, context):
        return LoginUser(request, context).__call__()

    def GenerateMobileOTP(self, request, context):
        return GenerateMobileOTP(request, context).__call__()

    def ValidateMobileOTP(self, request, context):
        return ValidateMobileOTP(request, context).__call__()

    def GetUserList(self, request, context):
        return GetUserList(request, context).__call__()

    def EditUserDetail(self, request, context):
        return EditUserDetail(request, context).__call__()

    def AuthenticateUserViaJWT(self, request, context):
        return AuthenticateUserViaJWT(request, context).__call__()

    def GetUserIDsDetail(self, request, context):
        return GetUserIDsDetail(request, context).__call__()


@contextmanager
def serve_forever(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:{}'.format(port))
    server.start()
    yield
    server.wait_for_termination()


class Command(BaseCommand):
    help = "GRPC API Server"

    def add_arguments(self, parser):
        parser.add_argument('port', nargs='+', type=int)

    def handle(self, *args, **options):
        port = options.get("port", 8000)[0]
        with serve_forever(port):
            print("Started gRPC server 0.0.0.0:{}".format(port), flush=True)
            try:
                while True:
                    time.sleep(60 * 60 * 24)
            except KeyboardInterrupt:
                pass
