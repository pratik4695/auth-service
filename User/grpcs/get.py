from django.db import transaction
from django.db.models import Q

from authentication.models import User, UserPermission
from authentication.models.permission import ObjectPermission, AccessObject
from authentication.serializers.get import UserBasicDataSerializer
from authentication.serializers.user import UserShortSerializer, UserSerializer
from authentication.services.helper import generate_random_password
from authentication.tasks import UserCreatedEmailNotification
from core.grpc import UnaryGRPC
from core.grpc_exceptions import ValidationError
from staffing_user_pb2 import Userdata
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class GetUser(UnaryGRPC):
    requires_authentication = False
    response_proto = Userdata

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for getting the user details with data - %s" % data)

        if not data.get("email", None):
            raise ValidationError("Please provide the email id")

        try:
            user = User.objects.get(email=data["email"])
            serializer = UserBasicDataSerializer(user)
            user_data = serializer.data
            return user_data
        except User.DoesNotExist:
            raise ValidationError("No existing user with email - {}".format(data["email"]))


class GetUserOrCreateUser(UnaryGRPC):
    response_proto = Userdata
    user_id_field = "created_by"

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def create_permissions(self, data, org_user_role_id):
        filter_query = []
        if not data.get("permissions"):
            return

        for perm in data["permissions"]:
            if not perm.get("name"):
                raise ValidationError("Permissions name is needed")

            if perm.get("sub_permissions"):
                for sub_perm in perm["sub_permissions"]:
                    filter_query.append(Q(name=sub_perm, parent_object__name=perm["name"]))
            else:
                filter_query.append(Q(name=perm["name"]))

        if not filter_query:
            return
        query = filter_query.pop()

        for fq in filter_query:
            query |= fq

        access_objects = AccessObject.objects.filter(query)

        permission_ids = []
        for acc_objs in access_objects:
            permission, created = ObjectPermission.objects.get_or_create(object_id=acc_objs.id)
            permission_ids.append(permission.id)

        if permission_ids:
            bulk_org_perm = [UserPermission(org_user_role_id=org_user_role_id, permission_id=perm_id,
                                            created_by=self.user_json) for perm_id in permission_ids]

            if bulk_org_perm:
                UserPermission.objects.bulk_create(bulk_org_perm)

    def update_permissions(self, user, new_permissions):
        user_permissions = user.permissions.all().values_list('object_id', flat=True)
        print("This is the user_permissions == {}".format(user_permissions))
        print("This is the new_permissions == {}".format(new_permissions))
        add_permissions = list(set(new_permissions) - set(user_permissions))
        delete_permissions = list(set(user_permissions) - set(new_permissions))

        if delete_permissions:
            UserPermission.objects.filter(user_id=user.id, permission_id__in=delete_permissions).delete()

        if add_permissions:
            bulk_user_perm = [UserPermission(user_id=user.id, permission_id=perm_id, created_by=self.user_json) for
                              perm_id in add_permissions]
            if bulk_user_perm:
                UserPermission.objects.bulk_create(bulk_user_perm)

    def run_logic(self, data):
        log.info("Received request for fetching or creating a user - %s" % data)
        is_new_record = False

        if not data.get("email", None):
            raise ValidationError("Please provide the email id")

        new_permissions = data.pop("permissions", [])

        try:
            user = User.objects.get(email=data["email"])
            user.decrypt_data()
            self.update_permissions(user, new_permissions)

            if (data["email"] == user.email and data.get("mobile") == user.mobile and data[
                "first_name"] == user.first_name and data["last_name"] == user.last_name and data[
                "user_role_id"] == user.user_role_id):
                self.update_permissions(user, new_permissions)
                user_serializer = UserBasicDataSerializer(instance=user)
                print("This is the response for the user == {}".format(user_serializer.data))
                print("This is the user_dict == {}".format(user.__dict__))
                return user_serializer.data
            data.pop("id", None)
            data["modified_by"] = self.user_json
            user_serializer = UserSerializer(instance=user, data=data)
        except User.DoesNotExist:
            if not data.get("id"):
                is_new_record = True
                data['password'] = generate_random_password(length=9)
                user_serializer = UserSerializer(data=data)
            else:
                try:
                    user = User.objects.get(id=data.get("id"))
                    user_serializer = UserSerializer(instance=user, data=data)
                except User.DoesNotExist:
                    print("No user found with user id == {}".format(data["existing_user_id"]))
                    return {}
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        self.update_permissions(user, new_permissions)
        user_serializer = UserBasicDataSerializer(instance=user)
        if is_new_record:
            transaction.on_commit(UserCreatedEmailNotification(data['password'], str(user.id)))
        print("This is the response for the user == {}".format(user_serializer.data))
        print("This is the user_dict == {}".format(user.__dict__))
        return user_serializer.data

# class ListUserShort(UnaryGRPC):
#     response_proto = UserListShortResponse
#
#     # def perform_authentication(self, user):
#     #     if not user or user.user_type != "PA":
#     #         return False
#     #     return True
#
#     def run_logic(self, data):
#         log.info("Received request for fetching list of organization user role - %s" % data)
#
#         if data.get("ids"):
#             user = User.objects.filter(id__in=data["ids"]).select_related('user_role').prefetch_related('permissions')
#         else:
#             user = User.objects.all().select_related('user_role').prefetch_related('permissions')
#
#         serializer = ListOrganizationUserRoleSerializer(org_user_roles, many=True)
#
#         response = {
#             "organization_user_roles": serializer.data
#         }
#         print("This is the response = {}".format(response))
#
#         return response
