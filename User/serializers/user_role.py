from rest_framework import serializers
from rest_framework.fields import UUIDField, CharField, DecimalField, BooleanField, IntegerField
from rest_framework.serializers import ModelSerializer

from authentication.constants import ObjectChoicesValueLabelMapping
from authentication.models import User
from authentication.models.user_roles import UserRole, OrganizationUserRole
from core.grpc_exceptions import ValidationError


class UserRoleSerializer(ModelSerializer):
    parent_role_id = IntegerField(required=False)

    class Meta:
        model = UserRole
        fields = ['id', 'name', 'parent_role_id', 'employee_visibility']


class OrganizationUserRoleSerializer(ModelSerializer):
    organization_id = UUIDField(required=True)
    user_role_id = IntegerField(required=False)
    parent_role_id = IntegerField(required=False)

    class Meta:
        model = OrganizationUserRole
        fields = ['id', 'organization_id', 'user_role_id', 'parent_role_id', 'name', 'employee_visibility',
                  'created_by', 'modified_by']


class ListOrganizationUserRoleSerializer(ModelSerializer):
    permissions = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    parent_role = serializers.SerializerMethodField()
    number_of_users = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationUserRole
        fields = ['id', 'user_role', 'parent_role', 'name', 'employee_visibility', 'permissions', 'number_of_users']

    def get_permissions(self, obj):
        permissions = obj.permissions.all()
        permission_list = [ObjectChoicesValueLabelMapping[perm.object.name] for perm in permissions if
                           not perm.object.parent_object]

        return permission_list

    def get_user_role(self, obj):
        ret_dict = {}
        if obj.user_role:
            ret_dict = {
                "id": obj.user_role.id,
                "name": obj.user_role.name
            }
        return ret_dict

    def get_parent_role(self, obj):
        ret_dict = {}
        if obj.parent_role:
            ret_dict = {
                "id": obj.parent_role.id,
                "name": obj.parent_role.name
            }
        return ret_dict

    def get_number_of_users(self, obj):
        count = User.objects.filter(user_role_id=obj.id).count()
        return count


class OrganizationUserRoleDetailedSerializer(ModelSerializer):
    permissions = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    parent_role = serializers.SerializerMethodField()

    # number_of_users = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationUserRole
        fields = ['id', 'name', 'user_role', 'parent_role', 'employee_visibility', 'permissions']

    def get_permissions(self, obj):
        permissions = obj.permissions.all()
        permission_list = [perm.id for perm in permissions]

        return permission_list

    def get_user_role(self, obj):
        ret_dict = {}
        if obj.user_role:
            ret_dict = {
                "id": obj.user_role.id,
                "name": obj.user_role.name
            }
        return ret_dict

    def get_parent_role(self, obj):
        ret_dict = {}
        if obj.parent_role:
            ret_dict = {
                "id": obj.parent_role.id,
                "name": obj.parent_role.name
            }
        return ret_dict


class BasicOrganizationUserRoleDetailSerializer(ModelSerializer):
    class Meta:
        model = OrganizationUserRole
        fields = ['id', 'name']


class ListUserRoleSerializer(ModelSerializer):
    permissions = serializers.SerializerMethodField()
    parent_role = serializers.SerializerMethodField()

    class Meta:
        model = UserRole
        fields = ['id', 'parent_role', 'name', 'employee_visibility', 'permissions']

    def get_permissions(self, obj):
        permissions = obj.permissions.all()
        permission_list = [perm.id for perm in permissions]

        return permission_list

    def get_parent_role(self, obj):
        ret_dict = {}
        if obj.parent_role:
            ret_dict = {
                "id": obj.parent_role.id,
                "name": obj.parent_role.name
            }
        return ret_dict
