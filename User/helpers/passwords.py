import json
import datetime
# import jwt
# from django.conf import settings

from django.utils import timezone
from authentication.models.passwords import PasswordResetToken
from authentication.serializers.passwords import PasswordResetTokenSerializer
from core.grpc_exceptions import ValidationError
from utils import encdec

PASSWORD_RESET_LINK_EXPIRE_DAYS = 1


def generate_token(user):
    if not user:
        return {}

    token_obj = PasswordResetToken.objects.filter(user_id=user.id, expires__gte=timezone.now())
    hash_code = generate_hash_code(user)

    if token_obj:
        if token_obj.count() > 1:
            raise ValidationError("Multiple token objects returned")
        token_obj = token_obj[0]

        token_serializer = PasswordResetTokenSerializer(instance=token_obj, data={"hash_code": hash_code},
                                                        partial=True)
    else:
        data = {
            "hash_code": hash_code,
            "expires": datetime.datetime.utcnow() + datetime.timedelta(days=PASSWORD_RESET_LINK_EXPIRE_DAYS),
            "user": user.id
        }
        token_serializer = PasswordResetTokenSerializer(data=data)

    token_serializer.is_valid(raise_exception=True)
    token_serializer.save()

    return {
        "hash_code": token_serializer.data.get("hash_code"),
        "expires": token_serializer.data.get("expires")
    }


def generate_hash_code(user):
    hash_code_payload = {
        "id": str(user.id),
        "name": user.name,
        "user_type": user.user_type,
        "expires": str(datetime.datetime.utcnow() + datetime.timedelta(days=PASSWORD_RESET_LINK_EXPIRE_DAYS))
    }
    # hash_code = jwt.encode(hash_code_payload, settings.ENCRYPT_KEY, algorithm='HS256').decode('utf-8')
    hash_code = encdec.MD5_Hash(json.dumps(hash_code_payload))
    return hash_code
