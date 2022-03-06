from User.models import User
from User.services.helper import generate_random_password
from core.grpc import UnaryGRPC
from core.grpc_exceptions import ValidationError
from staffing_user_pb2 import BooleanResponse
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class BulkCreateUser(UnaryGRPC):
    response_proto = BooleanResponse
    user_id_field = "created_by"

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for bulk creation of users - %s" % data)
        response = {"success": False}
        bulk_user_data = []

        try:
            for dict_ in data['users']:
                if not dict_.get("email", None):
                    raise ValidationError("Please provide the email id")

                password = generate_random_password(length=9)
                print("Users == {} -> Password == {}".format(dict_["email"], password))

                bulk_user_data.append(User(
                    email=dict_.get("email"),
                    mobile=dict_.get("mobile"),
                    first_name=dict_.get("first_name"),
                    last_name=dict_.get("last_name"),
                    user_type=dict_.get("user_type"),
                    password=password,
                    created_by=self.user_json
                ))

            User.objects.bulk_create(bulk_user_data)
            response["success"] = True
        except Exception as e:
            print("This is the exception in bulk creating == ", e)

        return response
