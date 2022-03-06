from django.utils import timezone
from django.db import transaction
from authentication.helpers.attendance import get_active_reporting_manager_with_email_id
from authentication.helpers.passwords import generate_token
from authentication.models import User
from authentication.models.passwords import PasswordResetToken
from authentication.serializers.login import UserLoginWithPasswordSerializer
from authentication.tasks.passwords import PasswordResetEmailNotificationToUser
from core.grpc import UnaryGRPC
from core.grpc_exceptions import ValidationError
from staffing_user_pb2 import BooleanResponse
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class ResetReportingManagerPasswordWithEmail(UnaryGRPC):
    requires_authentication = False
    response_proto = BooleanResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for resetting the password of user - %s" % data)

        email = data.get('email')
        password = data.get('password')
        new_password = data.pop('new_password', None)

        if not (email or password):
            raise ValidationError("Please provide Email id and Password")

        if not new_password:
            raise ValidationError("Please provide new Password")

        reporting_manager = get_active_reporting_manager_with_email_id(email)

        data["user_id"] = reporting_manager.get("user_id")

        login_serializer = UserLoginWithPasswordSerializer(data=data)
        is_valid = login_serializer.is_valid(raise_exception=True)

        if not is_valid:
            raise ValidationError(
                "Failed while changing password with error: {}".format(login_serializer.errors))

        user = reporting_manager.user
        user._set_password(new_password)
        user.save()

        return {"success": True}


class ResetReportingManagerPasswordWithLogin(UnaryGRPC):
    response_proto = BooleanResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for resetting the password of user - %s" % data)

        user_id = self.user_json.get("id", None)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            raise ValidationError("Invalid User")

        if not data.get("new_password"):
            raise ValidationError("Please provide the new password")

        user._set_password(data["new_password"])
        user.save()

        return {"success": True}


class CreateUserPasswordStaffing(UnaryGRPC):
    requires_authentication = False
    response_proto = BooleanResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for resetting the password of user via link - %s" % data)

        hash_code = data.get('hash_code')
        # user_id = data.get('user_id')
        new_password = data.pop('new_password', None)

        if not hash_code:
            raise ValidationError("Please provide required details")

        if not new_password:
            raise ValidationError("Please provide new Password")

        prt_obj = PasswordResetToken.objects.filter(hash_code=hash_code, expires__gte=timezone.now())

        if not prt_obj:
            raise ValidationError("Not a valid hash for given user")

        if len(prt_obj) > 1:
            raise ValidationError("Multiple token exists for the same code. Please contact the backend team.")

        user = prt_obj[0].user
        user._set_password(new_password)
        user.save()

        return {"success": True}


class SendUserPasswordResetEmailStaffing(UnaryGRPC):
    requires_authentication = False
    response_proto = BooleanResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for password reset email for user - %s" % data)

        user_id = data.get("id", None)
        try:
            user = User.objects.get(id=user_id)
            user.decrypt_data()
        except User.DoesNotExist:
            raise ValidationError("Invalid User id provided")

        if not user.email:
            raise ValidationError("No email is present for the user")

        password_reset_token = generate_token(user)

        PasswordResetEmailNotificationToUser(user, password_reset_token)()

        return {"success": True}
