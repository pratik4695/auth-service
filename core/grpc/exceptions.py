import json
import logging
import uuid

import grpc
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from core.grpc_exceptions import GrpcException


def parse_drf_error(error: dict):
    data = {}
    for key, value in error.items():
        if isinstance(value, dict):
            sub_data = parse_drf_error(value)
            for sub_key, sub_value in sub_data.items():
                data[".".join([key, sub_key])] = sub_value
        else:
            data[key] = value
    return data


class GRPCExceptionHandler:
    def __init__(self, context):
        self.context = context

    @staticmethod
    def _drf_validation_error(exc):
        error_code = grpc.StatusCode.FAILED_PRECONDITION
        if not hasattr(exc, "detail"):
            return error_code, json.dumps([str(exc)])
        if not isinstance(exc.detail, dict):
            return error_code, json.dumps([exc.detail])
        errors = []
        parsed_error = parse_drf_error(exc.detail)
        for key, value in parsed_error.items():
            if key == "non_field_errors":
                errors += value
                continue
            for _ in value:
                errors.append("{}: {}".format(key, _))
        return error_code, json.dumps(errors)

    def __call__(self, exc, stack):
        if issubclass(exc.__class__, GrpcException):
            code, message = exc.grpc_status, exc.message
        elif isinstance(exc, DRFValidationError):
            code, message = self._drf_validation_error(exc)
        elif isinstance(exc, ObjectDoesNotExist):
            code, message = grpc.StatusCode.NOT_FOUND, str(exc)
        elif isinstance(exc, DjangoValidationError):
            code, message = grpc.StatusCode.FAILED_PRECONDITION, str(exc)
        else:
            error_id = str(uuid.uuid4())
            code, message = grpc.StatusCode.INTERNAL, {"message": str(exc), "errorId": error_id}
            logging.warning("[ErrorID: {}]: {}".format(error_id, stack))
        self.context.set_code(code)
        if isinstance(message, dict) or isinstance(message, list):
            message = json.dumps(message)
        self.context.set_details(message)
        return self.context
