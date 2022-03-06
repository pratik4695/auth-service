from authentication.master_data_mappings import permissions_mapping_dictionary
from authentication.models.permission import AccessObject, ObjectPermission


def run(*args):
    access_object_ids = []
    for perm_name in permissions_mapping_dictionary:
        acc_obj = AccessObject.objects.create(name=perm_name)
        access_object_ids.append(acc_obj.id)
        if permissions_mapping_dictionary[perm_name]:
            for sub_perm_name in permissions_mapping_dictionary[perm_name]:
                sub_acc_obj = AccessObject.objects.create(name=sub_perm_name, parent_object_id=acc_obj.id)
                access_object_ids.append(sub_acc_obj.id)

    bulk_object_permissions = [ObjectPermission(object_id=obj_id) for obj_id in access_object_ids]

    if bulk_object_permissions:
        ObjectPermission.objects.bulk_create(bulk_object_permissions)

    print('========== Creating master data for permissions successful ==========')
