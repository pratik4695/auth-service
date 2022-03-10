from User.models import User
from User.serializers.user import UserListSerializer
from core.grpc import UnaryGRPC
from auth_service_pb2 import UserListResponse
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class GetUserList(UnaryGRPC):
    response_proto = UserListResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for fetching list of user - %s" % data)

        users = User.objects.all().prefetch_related('user_jwt')

        serializer = UserListSerializer(users, many=True)

        response = {
            "users": serializer.data
        }
        print("This is the response = {}".format(response))

        return response
