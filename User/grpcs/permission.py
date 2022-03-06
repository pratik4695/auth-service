from django.db import transaction

from authentication.models.permission import ObjectPermission
from authentication.serializers.permission import ObjectPermissionListSerializer
from core.grpc import UnaryGRPC
from core.grpc_exceptions import ValidationError
from staffing_user_pb2 import ObjectPermissionsListResponse
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class ListObjectPermissions(UnaryGRPC):
    response_proto = ObjectPermissionsListResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    @transaction.atomic
    def run_logic(self, data):
        log.info("Received request for fetching list of object permissions - %s" % data)

        object_permissions = ObjectPermission.objects.all().select_related("object")
        serializer = ObjectPermissionListSerializer(object_permissions, many=True)

        response = {
            "permissions": serializer.data
        }
        print("This is the response = {}".format(response))

        return response
