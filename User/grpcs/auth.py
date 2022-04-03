import datetime

import jwt
from django.conf import settings

from User.models import User
from User.serializers.user import UserShortSerializer
from core.grpc import UnaryGRPC
from auth_service_pb2 import AuthorisationResponse
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class AuthenticateUserViaJWT(UnaryGRPC):
    response_proto = AuthorisationResponse

    def run_logic(self, data):
        log.info("Received request for validating the user - %s" % data)
        response = {"user": {}, "status": {}}
        token = data.get("token")

        # import pdb
        # pdb.set_trace()
        payload = jwt.decode(token, settings.ENCRYPT_KEY, algorithms=['HS256'])
        # email = payload['email']
        userid = payload['id']

        try:
            user = User.objects.get(id=userid, is_active=True)
        except User.DoesNotExist:
            response["status"] = {"error_message": "No user exist", "status_code": 500, "success": False}
            return response

        try:
            token = user.user_jwt.get(access_token=token)
        except Exception as e:
            response["status"] = {"error_message": "Token mismatch", "status_code": 401, "success": False}
            return response

        if token.is_expired():
            response["status"] = {"error_message": "Token is invalid", "status_code": 403, "success": False}
            return response

        user_data = UserShortSerializer(instance=user)

        response["user"] = user_data.data
        response["status"] = {"error_message": "", "status_code": 200, "success": True}
        return response
