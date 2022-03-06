from rest_framework.fields import UUIDField, CharField, DecimalField, BooleanField, IntegerField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from authentication.constants import ObjectChoicesValueLabelMapping
from authentication.models import ObjectPermission


class ObjectPermissionListSerializer(ModelSerializer):
    name = SerializerMethodField()
    parent_name = SerializerMethodField()

    class Meta:
        model = ObjectPermission
        fields = ['id', 'name', 'parent_name']

    def get_name(self, obj):
        if obj.object:
            return ObjectChoicesValueLabelMapping.get(obj.object.name)

    def get_parent_name(self, obj):
        if obj.object and obj.object.parent_object:
            return ObjectChoicesValueLabelMapping.get(obj.object.parent_object.name)
