import json
import traceback
from abc import ABC

import grpc
from django.db import transaction
from django.db.models import Model
from rest_framework.serializers import ModelSerializer

from core import protobuf_to_dict, dict_to_protobuf
from core.grpc.exceptions import GRPCExceptionHandler
from core.grpc_exceptions import NotAuthenticated, PermissionDenied, GrpcException
from core.logger import GRPCLogger


class RequestUser:
    def __init__(self, data):
        assert data.get("id"), "Missing \'id\' in request user jwt token."
        self.id = data.get("id")
        self.user_type = data.get("user_type")
        self.entity_id = data.get("entity_id")
        self.employee_id = data.get("employee_id")


class UnaryGRPC:
    # The generated protocol buffer class which the rpc returns
    response_proto = None
    # The field name on which the request user JSON will be assigned
    user_id_field = None
    requires_authentication = False
    doc_modifiers = []
    client = None

    # Add methods here if post-processing is required on the results

    def __init__(self, request, context):
        assert self.response_proto, "Missing \'response_proto\' declaration."
        # Convert from generated proto object to dict/list
        self.request = type('Request', (object,), {})
        self.request.stream = []
        if isinstance(request, grpc._server._RequestIterator):
            req_list = []
            for r in request:
                req = protobuf_to_dict(r)
                req_list.append(req)
            self.request.stream = req_list
        else:
            self.request.data = protobuf_to_dict(request)

        # self.request = protobuf_to_dict(request)
        user_json = json.loads(dict(context.invocation_metadata()).get("user", "{}"))
        self.user_json = user_json

        if not self.user_json or not len(self.user_json):
            self.user = None
        else:
            self.user = RequestUser(self.user_json)
            self._populate_name_fields(self.user_json)

        if self.user_id_field and self.user:
            # Pop the expires keyword
            self.user_json.pop("expires", None)
            if getattr(self.request, 'stream'):
                for data in self.request.stream:
                    data[self.user_id_field] = self.user_json
            else:
                self.request.data[self.user_id_field] = self.user_json
        self.context = context
        # Auth Header of the form: Bearer <jwt_token>
        self.auth_header = dict(context.invocation_metadata()).get("authheader", None)

    @staticmethod
    def _populate_name_fields(user_json):
        if user_json.get('name') and (not user_json.get('first_name') and not user_json.get('last_name')):
            if len(user_json['name'].split()) > 1:
                user_json['first_name'], user_json['last_name'] = user_json['name'].split(maxsplit=1)
            else:
                user_json['first_name'] = user_json['name']
        if not user_json.get('name') and (user_json.get('first_name') or user_json.get('last_name')):
            user_json['name'] = " ".join([user_json.get('first_name', ''), user_json.get('last_name', '')]).strip()

    def validate(self, data):
        return data

    def perform_authentication(self, user):
        return True

    def set_up_pymongo_connection(self, collection_name):
        self.client = pymongo.MongoClient(
            "mongodb+srv://mystock_base:mystocks123@startupcluster.lknul.mongodb.net/MyStocks_db?retryWrites=true&w=majority")
        db = self.client.MyStocks_db
        return db[collection_name]

    def close_pymongo_connection(self):
        if self.client:
            self.client.close()

    def run_logic(self, data):
        raise NotImplementedError("Override \'run_logic\'.")

    def _handle_exception(self, exc, stack):
        self.context = GRPCExceptionHandler(self.context)(exc, stack)

    def __call__(self):
        with GRPCLogger(self.__class__.__qualname__, self.request) as log:
            try:
                if self.requires_authentication and not self.user:
                    raise NotAuthenticated
                if not self.perform_authentication(self.user):
                    raise PermissionDenied
                with transaction.atomic():
                    if getattr(self.request, 'data'):
                        request_data = self.request.data
                    elif getattr(self.request, 'stream'):
                        request_data = self.request.stream
                    else:
                        request_data = {}
                    validated_data = self.validate(request_data)
                    result = self.run_logic(validated_data)
                for doc_modifier in self.doc_modifiers:
                    result = doc_modifier(result)
                return dict_to_protobuf(self.response_proto, values=result, ignore_none=True)
            except Exception as ex:
                self._handle_exception(ex, traceback.format_exc())
                return self.response_proto()

    def get_stream_response(self):
        with GRPCLogger(self.__class__.__qualname__, self.request) as log:
            try:
                if self.requires_authentication and not self.user:
                    raise NotAuthenticated
                if not self.perform_authentication(self.user):
                    raise PermissionDenied
                if getattr(self.request, 'data'):
                    request_data = self.request.data
                elif getattr(self.request, 'stream'):
                    request_data = self.request.stream
                else:
                    request_data = {}
                # request_data = self.request.data if getattr(self.request, 'data') else getattr(self.request, 'stream')
                validated_data = self.validate(request_data)
                result = self.run_logic(validated_data)

                for individual_object in result:
                    for doc_modifier in self.doc_modifiers:
                        individual_object = doc_modifier(individual_object)
                    yield dict_to_protobuf(self.response_proto, values=individual_object, ignore_none=True)

            except Exception as ex:
                self._handle_exception(ex, traceback.format_exc())
                return self.response_proto()


class ListModelGRPC(UnaryGRPC):
    SERIALIZER_CLASS: ModelSerializer.__class__ = None
    MODEL_CLASS: Model.__class__ = None

    def get_queryset(self, data):
        return self.MODEL_CLASS.objects.all()

    def run_logic(self, data):
        queryset = self.get_queryset(data)
        serializer = self.SERIALIZER_CLASS(queryset, many=True)
        return serializer.data


class ServerStreamGRPCView(UnaryGRPC, ABC):
    serializer_class = None
    queryset = None

    def filter_queryset(self, request):
        return self.queryset

    def __call__(self):
        try:
            if self.requires_authentication and not self.user:
                raise NotAuthenticated
            if not self.perform_authentication(self.user):
                raise PermissionDenied
            self.validate()
            self.queryset = self.filter_queryset(self.request)
            objects = self.queryset
            for obj in objects:
                data = self.serializer_class(instance=obj).data
                yield dict_to_protobuf(self.response_proto, values=data, ignore_none=True)

        except Exception as ex:
            self._handle_exception(ex, traceback.format_exc())
            yield self.response_proto()


class RetrieveModelGRPC(UnaryGRPC):
    MODEL_CLASS: Model.__class__ = None
    SERIALIZER_CLASS: ModelSerializer.__class__ = None

    def get_object(self, data) -> Model:
        raise NotImplementedError

    def run_logic(self, data):

        try:
            model_instance = self.get_object(data)
        except Exception as e:
            raise GrpcException("Could not find {} instance for request_data: {} : {}".format(
                self.MODEL_CLASS.__class__.__name__, data, e))

        return self.SERIALIZER_CLASS(model_instance).data
