import datetime

from User.models import User
from User.serializers.login import UserLoginWithPasswordSerializer, UserLoginDataSerializer
from User.serializers.user import UserSerializer
from auth_service_pb2 import UserLoginResponse
from core.grpc import UnaryGRPC
from core.grpc_exceptions import ValidationError
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class RegisterUser(UnaryGRPC):
    response_proto = UserLoginResponse

    def perform_authentication(self, user):
        #     if not user or user.user_type != "PA":
        #         return False
        return True

    def validate_data(self, data):
        if not (data.get("first_name") and data.get("last_name")):
            raise ValidationError("Required Field: First name and last name")

        if not data.get("username"):
            raise ValidationError("Required Field: username")

        mobile = data.get("mobile")
        email = data.get("email")

        if not mobile:
            raise ValidationError("Required Field: Mobile")

        if not email:
            raise ValidationError("Required Field: Email")

        active_user_with_mobile_no_exist = User.objects.filter(mobile=mobile, is_active=True).exists()

        if active_user_with_mobile_no_exist:
            raise ValidationError("This mobile number is already active with us.")

        active_user_with_email_exist = User.objects.filter(email=email, is_active=True).exists()

        if active_user_with_email_exist:
            raise ValidationError("This email id is already active with us.")

        if not data.get("password"):
            raise ValidationError("Required Field: Password")

        if not data.get("re_password"):
            raise ValidationError("Required Field: re_password")

        if not (data["password"] == data["re_password"]):
            raise ValidationError("Password not matching")

        if not data.get("date_of_birth"):
            raise ValidationError("Required Field: date of birth")

        try:
            data["date_of_birth"] = datetime.datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()
        except:
            raise ValidationError("Date of Birth: Incorrect Format (yyyy-mm-dd)")

        data["is_active"] = True

    def run_logic(self, data):
        # import pdb
        # pdb.set_trace()
        log.info("Received request for registering the user - %s" % data)
        self.validate_data(data)
        user_serializer = UserSerializer(data=data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        login_data = {"email": data["email"], "password": data["password"]}

        login_serializer = UserLoginWithPasswordSerializer(data=login_data)
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
