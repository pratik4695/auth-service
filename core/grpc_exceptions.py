import grpc
from django.db import IntegrityError


class GrpcException(Exception):
    grpc_status = grpc.StatusCode.INTERNAL
    message = "Something Went Wrong."

    def __init__(self, message=None):
        if message:
            self.message = message


class PermissionDenied(GrpcException):
    grpc_status = grpc.StatusCode.PERMISSION_DENIED
    message = "Action not permitted."


class NotAuthenticated(GrpcException):
    grpc_status = grpc.StatusCode.UNAUTHENTICATED
    message = "Missing authentication"


class ObjectDoesNotExist(GrpcException):
    grpc_status = grpc.StatusCode.NOT_FOUND
    message = "Object not found."


class MissingArgument(GrpcException):
    grpc_status = grpc.StatusCode.INVALID_ARGUMENT
    message = "Missing required argument"


class ValidationError(GrpcException):
    grpc_status = grpc.StatusCode.FAILED_PRECONDITION
    message = "Validation error."


class UniqueConstraintFailed(GrpcException):
    grpc_status = grpc.StatusCode.ALREADY_EXISTS
    message = "Duplicate entry"

    @classmethod
    def check(cls, error: Exception):
        """
        Checks whether the database error received is due to unique constraint failure or not.
        :param error: Exception catched
        :return: True if unique constraint failure else False
        """
        if not isinstance(error, IntegrityError):
            return False
        if error.__cause__.pgcode == "23505":
            return True
        else:
            return False
