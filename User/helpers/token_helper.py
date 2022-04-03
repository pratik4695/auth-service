import datetime
import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from User.models import UserJWTToken
from User.serializers.token import UserJWTTokenSerializer

REFRESH_TOKEN_EXPIRE_DAYS = 15
ACCESS_TOKEN_EXPIRE_DAYS = 1


def generate_token(user):
    if not user:
        return {}

    token_obj = UserJWTToken.objects.filter(user_id=user.id, expires__gte=timezone.now())
    access_token = generate_access_token(user)

    if token_obj:
        if token_obj.count() > 1:
            raise ValidationError("Multiple token objects returned")
        token_obj = token_obj[0]

        token_serializer = UserJWTTokenSerializer(instance=token_obj, data={"access_token": access_token},
                                                  partial=True)
    else:
        data = {
            "access_token": access_token,
            "refresh_token": generate_refresh_token(user),
            "expires": datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "user": user.id
        }
        token_serializer = UserJWTTokenSerializer(data=data)

    token_serializer.is_valid(raise_exception=True)
    token_serializer.save()

    return {
        "access_token": token_serializer.data.get("access_token"),
        "refresh_token": token_serializer.data.get("refresh_token"),
        "expires": token_serializer.data.get("expires")
    }


def generate_access_token(user):
    user.decrypt_data()
    access_token_payload = {
        "id": str(user.id),
        "name": user.name,
        "user_type": user.user_type,
        "email": user.email,
        "expires": str(datetime.datetime.utcnow() + datetime.timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)),
    }
    access_token = jwt.encode(access_token_payload, settings.ENCRYPT_KEY, algorithm='HS256')
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'id': str(user.id),
        'expires': str(datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    }
    refresh_token = jwt.encode(refresh_token_payload, settings.ENCRYPT_KEY, algorithm='HS256')

    return refresh_token
