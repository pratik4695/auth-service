from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from authentication.models.user import User
from utils import encdec

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class UserBasicDataSerializer(ModelSerializer):
    """
        Created By: Pratik Gupta
        Created On: 24/05/2021
    """
    email = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user_type', 'first_name', 'last_name', 'email', 'mobile', 'user_role', 'permissions']

    def get_permissions(self, user):
        permissions = user.permissions.all()
        permission_list = [perm.id for perm in permissions]

        return permission_list

    def get_email(self, user):
        if user.email_encrypted:
            return encdec.DecodeAES(user.email_encrypted)
        return None

    def get_mobile(self, user):
        if user.mobile_encrypted:
            return encdec.DecodeAES(user.mobile_encrypted)
        return None

    def get_user_role(self, user):
        role_data = {}
        if user.user_role:
            role_data["id"] = user.user_role.id
            role_data["name"] = user.user_role.name
        return role_data
