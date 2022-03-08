import datetime
from random import randint

from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone

from User.constants import MOBILE_NUMBER_REGEX
from User.models import User
from User.models.user import MobileOTP
from User.serializers.login import UserLoginWithPasswordSerializer, UserLoginDataSerializer
from User.serializers.user import UserSerializer, MobileOTPSerializer
from auth_service_pb2 import UserLoginResponse, BooleanResponse
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


class GenerateMobileOTP(UnaryGRPC):
    response_proto = BooleanResponse

    def perform_authentication(self, user):
        #     if not user or user.user_type != "PA":
        #         return False
        return True

    def validate_data(self, data):
        mobile_validator = RegexValidator(regex=MOBILE_NUMBER_REGEX)
        mobile = data.get("mobile")

        try:
            mobile = mobile.strip() if (mobile and mobile.strip()) else None
            mobile_validator(mobile)
        except ValidationError:
            raise ValidationError("Invalid mobile number provided, expected {0}".format(MOBILE_NUMBER_REGEX))

        active_user_with_mobile_no_exist = User.objects.filter(mobile=mobile, is_active=True).exists()

        if active_user_with_mobile_no_exist:
            raise ValidationError("This mobile number is already active with us.")

    def generate_otp(self, mobile):
        # if mobile == settings.TEST_MOBILE:
        #     otp_code = str(settings.TEST_LOGIN_OTP)
        #     return otp_code
        opt_code = str(randint(100000, 999999))
        return opt_code

    def generate_access_otp(self, data):
        try:
            mobile_otp = MobileOTP.objects.get(temp_mobile=data["mobile"], access_otp_expiry__gt=timezone.now())
        except MobileOTP.DoesNotExist:
            gen_data = {
                "temp_mobile": data["mobile"],
                "access_otp": self.generate_otp(data["mobile"]),
                "access_otp_expiry": datetime.datetime.now() + datetime.timedelta(seconds=120)
            }
            ser = MobileOTPSerializer(data=gen_data)
            ser.is_valid(raise_exception=True)
            mobile_otp = ser.save()
        return mobile_otp

    def run_logic(self, data):
        import pdb
        pdb.set_trace()
        log.info("Received request for MobileOTP generation - %s" % data)
        self.validate_data(data)
        mobile_otp = self.generate_access_otp(data)
        mobile_otp.send_otp_via_2_factor()

        return {"success": True}


class ValidateMobileOTP(UnaryGRPC):
    response_proto = BooleanResponse

    def perform_authentication(self, user):
        #     if not user or user.user_type != "PA":
        #         return False
        return True

    def validate_data(self, data):
        mobile_validator = RegexValidator(regex=MOBILE_NUMBER_REGEX)
        mobile = data.get("mobile")

        try:
            mobile = mobile.strip() if (mobile and mobile.strip()) else None
            mobile_validator(mobile)
        except ValidationError:
            raise ValidationError("Invalid mobile number provided, expected {0}".format(MOBILE_NUMBER_REGEX))

        active_user_with_mobile_no_exist = User.objects.filter(mobile=mobile, is_active=True).exists()

        if active_user_with_mobile_no_exist:
            raise ValidationError("This mobile number is already active with us.")

    def validate_access_otp(self, data):
        try:
            mobile_otp = MobileOTP.objects.get(access_otp=data["otp"], temp_mobile=data["mobile"],
                                               access_otp_expiry__gte=timezone.now())
        except MobileOTP.DoesNotExist:
            raise ValidationError("Invalid OTP")

        return True

    def run_logic(self, data):
        log.info("Received request for MobileOTP generation - %s" % data)
        self.validate_data(data)
        mobile_otp = self.validate_access_otp(data)

        return {"success": True}
