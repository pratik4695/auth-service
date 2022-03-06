from authentication.models import User
from authentication.serializers.recognize_user import RecognizeUserSerializer
from core.grpc import UnaryGRPC
from core.grpc_exceptions import ValidationError
from staffing_user_pb2 import Userdata
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class RecognizeUserStaffing(UnaryGRPC):
    requires_authentication = False
    response_proto = Userdata

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for recognizing the user with data - %s" % data)

        if not data.get("email", None):
            raise ValidationError("Please provide the email id")

        try:
            user = User.objects.get(email=data["email"])
            serializer = RecognizeUserSerializer(user)
            user_data = serializer.data
            return user_data
        except User.DoesNotExist:
            raise ValidationError("No existing user with email - {}".format(data["email"]))
