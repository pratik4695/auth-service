import datetime

from User.models import User
from User.serializers.user import UserListSerializer, UserSerializer
from core.grpc import UnaryGRPC
from auth_service_pb2 import UserListResponse, BooleanResponse
from core.grpc_exceptions import ValidationError
from utils.logging import get_logger
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

log = get_logger(name=__file__, logging_level="INFO")


class GetUserList(UnaryGRPC):
    response_proto = UserListResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        # import pdb
        # pdb.set_trace()
        log.info("Received request for fetching list of user - %s" % data)

        users = User.objects.all().prefetch_related('user_jwt').order_by("created")
        page = data.get('page', 1)
        paginator = Paginator(users, 50)

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        serializer = UserListSerializer(users, many=True)

        response = {
            "users": serializer.data,
            "per_page": paginator.per_page,
            "orphans": paginator.orphans,
            "allow_empty_first_page": paginator.allow_empty_first_page,
            "count": paginator.count,
            "num_pages": paginator.num_pages

        }
        print("This is the response = {}".format(response))

        return response


class EditUserDetail(UnaryGRPC):
    response_proto = BooleanResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def validate_data(self, data):
        if not data.get("id"):
            raise ValidationError("Please provide the valid user id")

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

        # if not data.get("password"):
        #     raise ValidationError("Required Field: Password")
        #
        # if not data.get("re_password"):
        #     raise ValidationError("Required Field: re_password")

        # if not (data["password"] == data["re_password"]):
        #     raise ValidationError("Password not matching")

        if not data.get("date_of_birth"):
            raise ValidationError("Required Field: date of birth")

        try:
            data["date_of_birth"] = datetime.datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()
        except:
            raise ValidationError("Date of Birth: Incorrect Format (yyyy-mm-dd)")

        data["is_active"] = True

    def run_logic(self, data):
        log.info("Received request for updating the user detail - %s" % data)

        try:
            user = User.objects.get(id=data["id"])
        except User.DoesNotExist:
            raise ValidationError("No user exists with given id")

        user_serializer = UserSerializer(instance=user, data=data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        return {"success": True}
