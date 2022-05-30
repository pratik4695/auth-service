from dateutil.parser import parse
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from User.helpers.token_helper import generate_token
from User.models import User
from utils import encdec

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class UserLoginWithPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    access_token = serializers.CharField(max_length=400, read_only=True)
    refresh_token = serializers.CharField(max_length=400, read_only=True)
    expires = serializers.IntegerField(read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with given email and password does not exists')

        user = authenticate(username=user.id, password=password)
        if user is None:
            raise serializers.ValidationError(
                'Incorrect password. Please try again'
            )

        token = generate_token(user)

        return {
            'email': email,
            'access_token': token.get("access_token"),
            'refresh_token': token.get("refresh_token"),
            'expires': parse(token.get("expires")).timestamp()
        }


class UserLoginWithMobileSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    access_token = serializers.CharField(max_length=400, read_only=True)
    refresh_token = serializers.CharField(max_length=400, read_only=True)
    expires = serializers.IntegerField(read_only=True)

    def validate(self, data):
        email = data.get("email", None)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with given email and password does not exists')

        token = generate_token(user)

        return {
            'email': email,
            'access_token': token.get("access_token"),
            'refresh_token': token.get("refresh_token"),
            'expires': parse(token.get("expires")).timestamp()
        }


class UserLoginDataSerializer(ModelSerializer):
    """
    """
    email = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'user_type', 'user_full_name', 'first_name', 'last_name', 'email', 'mobile', 'username'
        )

    def get_email(self, user):
        if user.email_encrypted:
            return encdec.DecodeAES(user.email_encrypted)
        return None

    def get_mobile(self, user):
        if user.mobile_encrypted:
            return encdec.DecodeAES(user.mobile_encrypted)
        return None
