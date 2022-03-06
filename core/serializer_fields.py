from uuid import UUID

import datetime
from django.core.files.storage import default_storage
from month import Month
from rest_framework.fields import Field, CharField, DateField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer

from .helpers import get_absolute_url


class URLField(CharField):
    def __init__(self, attribute_name, **kwargs):
        self.attribute_name = attribute_name
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if not data:
            return None
        pre_url = default_storage.url("")
        if pre_url in data:
            data = data.replace(pre_url, "")
        return super().to_internal_value(data)

    def to_representation(self, value):
        value = super().to_representation(value)
        return get_absolute_url(value)


class ForeignKeyField(PrimaryKeyRelatedField):
    def __init__(self, attribute_name, **kwargs):
        if kwargs.get("many", False):
            raise AssertionError("'\many=True\' not allowed for this field.")
        self.attribute_name = attribute_name
        self.related_name = attribute_name
        self.execute_first = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        value = super().to_representation(value)
        if isinstance(value, UUID):
            return str(value)
        else:
            return value


class MonthField(DateField):
    def __init__(self, *args, **kwargs):
        kwargs["input_formats"] = ["%Y-%m"]
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if isinstance(value, Month):
            return value._date.strftime("%Y-%m")
        elif isinstance(value, datetime.date):
            return value.strftime("%Y-%m")
        else:
            return value


class DjangoRelatedField(Field):
    def __init__(self, related_name=None, serializer=None, parent_name=None, **kwargs):
        if serializer:
            assert issubclass(serializer, Serializer), '`serializer` should be subclass of Serializer'
            self.serializer = serializer
        self.parent_name = parent_name
        super().__init__(**kwargs)
        if related_name:
            self.related_name = related_name
        else:
            self.related_name = self.field_name

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        pass


class OneToOneField(DjangoRelatedField):
    def __init__(self, execute_first=False, **kwargs):
        self.execute_first = execute_first
        self.partial = False
        super().__init__(**kwargs)

    def to_representation(self, value):
        return self.serializer().to_representation(value)

    def to_internal_value(self, data):
        return self.serializer(partial=self.partial).to_internal_value(data)


class ManyToManyField(DjangoRelatedField):
    def __init__(self, serializer=None, queryset=None, **kwargs):
        assert not (serializer and queryset), "May not set both `serializer` and `queryset`"
        if serializer:
            self.serializer = serializer
        else:
            self.queryset = queryset
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if self.queryset:
            return PrimaryKeyRelatedField(queryset=self.queryset, many=True).to_internal_value(data)
        else:
            return self.serializer(many=True).to_internal_value(data)

    def to_representation(self, value):
        if self.queryset:
            return PrimaryKeyRelatedField(queryset=self.queryset, many=True).to_representation(value)
        else:
            return self.serializer(many=True).to_representation(value)


class OneToManyField(DjangoRelatedField):
    def __init__(self, unique_identifier="id", **kwargs):
        self.unique_identifier = unique_identifier
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        return self.serializer(many=True).to_internal_value(data)

    def to_representation(self, value):
        return self.serializer(many=True).to_representation(value)


class OneToManyGenericField(DjangoRelatedField):
    def __init__(self, unique_identifier="id", generic_foreign_key_field="content_object", **kwargs):
        self.unique_identifier = unique_identifier
        self.generic_foreign_key_field = generic_foreign_key_field
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        return self.serializer(many=True).to_internal_value(data)

    def to_representation(self, value):
        return self.serializer(many=True).to_representation(value)


