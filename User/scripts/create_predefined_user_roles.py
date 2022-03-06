from django.db.models import Q

from authentication.master_data_mappings import predefined_user_role_data
from authentication.models import UserRole, UserRolePermission
from authentication.models.permission import AccessObject, ObjectPermission


def run(*args):
    for data in predefined_user_role_data:
        filter_query = []
        permissions = data.pop("permissions")
        user_role = UserRole.objects.create(**data)
        print(user_role)

        for perm in permissions:
            if permissions[perm]:
                for sub_perm in permissions[perm]:
                    filter_query.append(Q(name=sub_perm, parent_object__name=perm))
            else:
                filter_query.append(Q(name=perm))

        if not filter_query:
            continue
        query = filter_query.pop()

        for fq in filter_query:
            query |= fq

        access_objects = AccessObject.objects.filter(query).values_list("id", flat=True)

        permission_ids = ObjectPermission.objects.filter(object_id__in=access_objects).values_list("id", flat=True)

        if permission_ids:
            bulk_org_perm = [UserRolePermission(user_role_id=user_role.id, permission_id=perm_id) for perm_id in
                             permission_ids]

            if bulk_org_perm:
                UserRolePermission.objects.bulk_create(bulk_org_perm)

    print('========== Master data creation for user role successful==========')
