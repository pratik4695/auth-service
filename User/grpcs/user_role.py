from django.db import IntegrityError, transaction
from django.db.models import Q

from authentication.models.permission import AccessObject, ObjectPermission
from authentication.models.user_roles import OrganizationUserRole, OrganizationUserRolePermission, UserRole
from authentication.serializers.user_role import OrganizationUserRoleSerializer, ListOrganizationUserRoleSerializer, \
    BasicOrganizationUserRoleDetailSerializer, ListUserRoleSerializer, OrganizationUserRoleDetailedSerializer
from core.grpc import UnaryGRPC
from core.grpc_exceptions import ValidationError
from staffing_user_pb2 import BooleanResponse, OrganizationUserRoleListResponse, OrganizationUserRoleResponse, \
    UserRoleListResponse, OrganizationUserRoleListShortResponse
from utils.logging import get_logger

log = get_logger(name=__file__, logging_level="INFO")


class AddOrganizationUserRole(UnaryGRPC):
    response_proto = OrganizationUserRoleResponse
    user_id_field = "created_by"

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def validate_data(self, data):
        if not data.get("name"):
            raise ValidationError("name: This field is required")

        if not data.get("employee_visibility"):
            raise ValidationError("employee_visibility: This field is required")

        data["organization_id"] = self.user.entity_id

        # if not data.get("parent_role_id"):
        #     raise ValidationError("parent_role_id: This field is required")

    def get_user_role_data(self, data):
        user_role_data = {
            "organization_id": data["organization_id"],
            "name": data["name"],
            "created_by": self.user_json,
            "modified_by": self.user_json,
            "employee_visibility": data["employee_visibility"]
        }

        if data.get("user_role_id"):
            user_role_data["user_role_id"] = data["user_role_id"]
        if data.get("parent_role_id"):
            user_role_data["parent_role_id"] = data["parent_role_id"]

        return user_role_data

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
            bulk_org_perm = [OrganizationUserRolePermission(org_user_role_id=org_user_role_id, permission_id=perm_id,
                                                            created_by=self.user_json) for perm_id in permission_ids]

            if bulk_org_perm:
                OrganizationUserRolePermission.objects.bulk_create(bulk_org_perm)

    def update_permissions(self, user_role, new_permissions):
        user_role_permissions = user_role.permissions.all().values_list('object_id', flat=True)
        print("This is the user_role_permissions == {}".format(user_role_permissions))
        print("This is the new_permissions == {}".format(new_permissions))
        add_permissions = list(set(new_permissions) - set(user_role_permissions))
        delete_permissions = list(set(user_role_permissions) - set(new_permissions))

        if delete_permissions:
            OrganizationUserRolePermission.objects.filter(org_user_role_id=user_role.id,
                                                          permission_id__in=delete_permissions).delete()

        if add_permissions:
            bulk_user_perm = [
                OrganizationUserRolePermission(org_user_role_id=user_role.id, permission_id=perm_id,
                                               created_by=self.user_json) for perm_id in add_permissions]
            if bulk_user_perm:
                OrganizationUserRolePermission.objects.bulk_create(bulk_user_perm)

    @transaction.atomic
    def run_logic(self, data):
        log.info("Received request for adding new user role - %s" % data)
        response = {"success": False}
        self.validate_data(data)
        org_user_role_data = self.get_user_role_data(data)
        if data.get("id"):
            try:
                org_usr_role = OrganizationUserRole.objects.get(id=data["id"])
                org_user_role_serializer = OrganizationUserRoleSerializer(instance=org_usr_role,
                                                                          data=org_user_role_data)
            except Exception as e:
                raise ValidationError("No Organization role with given id")
        else:
            org_user_role_serializer = OrganizationUserRoleSerializer(data=org_user_role_data)
        try:
            org_user_role_serializer.is_valid(raise_exception=True)
            org_user_role = org_user_role_serializer.save()
        except IntegrityError as e:
            print("Error while creating organization user role = {}".format(e))
            raise ValidationError('This User Role is already present.')

        print("This is org_user_role = {}".format(org_user_role))

        org_user_role_id = org_user_role.id

        self.update_permissions(org_user_role, data.get("permissions"))

        # org_user_role = OrganizationUserRole.objects.get(id=org_user_role_id)
        serializer = OrganizationUserRoleDetailedSerializer(org_user_role)
        response = serializer.data
        # response = org_user_role.serialize_organization_user_role()
        print("This is the response == {}".format(response))
        return response


class GetOrganizationUserRole(UnaryGRPC):
    response_proto = OrganizationUserRoleResponse
    user_id_field = "created_by"

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    @transaction.atomic
    def run_logic(self, data):
        log.info("Received request for fetching user role - %s" % data)
        if not data.get("id"):
            raise ValidationError("Need id for fetching data")

        try:
            org_user_role = OrganizationUserRole.objects.get(id=data["id"])
        except OrganizationUserRole.DoesNotExist:
            raise ValidationError("Please provide valid id")

        serializer = OrganizationUserRoleDetailedSerializer(org_user_role)
        response = serializer.data
        print("This is the response == {}".format(response))

        return response


class ListOrganizationUserRole(UnaryGRPC):
    response_proto = OrganizationUserRoleListResponse
    user_id_field = "created_by"

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    @transaction.atomic
    def run_logic(self, data):
        log.info("Received request for fetching list of organization user role - %s" % data)
        organization_id = self.user.entity_id

        org_user_roles = OrganizationUserRole.objects.filter(organization_id=organization_id).prefetch_related(
            'permissions')
        serializer = ListOrganizationUserRoleSerializer(org_user_roles, many=True)

        # try:
        #     org_user_role = OrganizationUserRole.objects.get(id=data["id"])
        # except OrganizationUserRole.DoesNotExist:
        #     raise ValidationError("Please provide valid id")

        response = {
            "organization_user_roles": serializer.data
        }
        print("This is the response = {}".format(response))

        return response


class ListOrganizationUserRoleShort(UnaryGRPC):
    response_proto = OrganizationUserRoleListShortResponse

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    def run_logic(self, data):
        log.info("Received request for fetching list of organization user role - %s" % data)

        if not data.get("organization_id"):
            raise ValidationError("Need organization id for fetching data")

        if data.get("ids"):
            org_user_roles = OrganizationUserRole.objects.filter(organization_id=data["organization_id"],
                                                                 id__in=data["ids"]).prefetch_related(
                'permissions')
        else:
            org_user_roles = OrganizationUserRole.objects.filter(
                organization_id=data["organization_id"]).prefetch_related(
                'permissions')
        serializer = ListOrganizationUserRoleSerializer(org_user_roles, many=True)

        response = {
            "organization_user_roles": serializer.data
        }
        print("This is the response = {}".format(response))

        return response


class ListUserRole(UnaryGRPC):
    response_proto = UserRoleListResponse
    user_id_field = "created_by"

    # def perform_authentication(self, user):
    #     if not user or user.user_type != "PA":
    #         return False
    #     return True

    @transaction.atomic
    def run_logic(self, data):
        log.info("Received request for fetching list of organization user role - %s" % data)

        org_user_roles = UserRole.objects.all().prefetch_related('permissions')
        serializer = ListUserRoleSerializer(org_user_roles, many=True)

        response = {
            "user_roles": serializer.data
        }
        print("This is the response = {}".format(response))

        return response

# class GetUserRole(UnaryGRPC):
#     response_proto = OrganizationUserRoleResponse
#
#     # def perform_authentication(self, user):
#     #     if not user or user.user_type != "PA":
#     #         return False
#     #     return True
#
#     @transaction.atomic
#     def run_logic(self, data):
#         log.info("Received request for fetching user role - %s" % data)
#         if not data.get("id"):
#             raise ValidationError("Need id for fetching data")
#
#         try:
#             user_role = UserRole.objects.get(id=data["id"])
#         except UserRole.DoesNotExist:
#             raise ValidationError("Please provide valid id")
#
#         response = user_role.serialize_organization_user_role()
#
#         return response
