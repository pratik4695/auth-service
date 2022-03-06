from User.models import User
from User.serializers.login import UserLoginWithPasswordSerializer, UserLoginDataSerializer
from auth_service_pb2 import UserLoginResponse
from core.grpc import UnaryGRPC
from core.grpc_exceptions import ValidationError
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class LoginUser(UnaryGRPC):
    requires_authentication = False
    response_proto = UserLoginResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for login of User - %s" % data)

        email_id = data.get('email')
        password = data.get('password')

        if not (email_id or password):
            raise ValidationError("Provide Email id and Password")

        try:
            user = User.objects.get(email=email_id)
        except Exception as e:
            raise ValidationError("This email id does not exist")

        login_serializer = UserLoginWithPasswordSerializer(data=data)
        login_serializer.is_valid(raise_exception=True)

        user_data = UserLoginDataSerializer(instance=user)

        response = {
            "token": {
                "access_token": login_serializer.data["access_token"],
                "refresh_token": login_serializer.data["refresh_token"],
                "expires": login_serializer.data["expires"]
            },
            "user": user_data.data
        }

        print("This is the response = {}".format(response))

        return response
