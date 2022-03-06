from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.db.models import Model
from rest_framework.fields import SkipField
from rest_framework.fields import set_value
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError

from .serializer_fields import OneToOneField, ManyToManyField, OneToManyField, DjangoRelatedField, \
    ForeignKeyField, URLField, OneToManyGenericField


class DjangoModelSerializer(ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.one2one_fields = OrderedDict()
        self.m2m_fields = OrderedDict()
        self.one2m_fields = OrderedDict()
        self.one2m_generic_fields = OrderedDict()
        super().__init__(*args, **kwargs)

    @staticmethod
    def handle_one_to_one_field(data, field, instance):
        """
        Creates One to One object after the instance is created.
        :param data: validated data
        :param field: serializer field object
        :param instance: the parent instance
        """
        if not data:
            return None
        if hasattr(instance, field.related_name):
            related_instance = getattr(instance, field.related_name)
            field.serializer(partial=True).update(related_instance, data)
        else:
            data[field.parent_name] = instance
            field.serializer().create(data)

    @staticmethod
    def handle_m2m_field(data, instance, field):
        if not data:
            return None
        assert isinstance(data, (tuple, list)), "`data` should be a list or tuple."
        related_queryset = getattr(instance, field.related_name)
        # Clear the previous set first
        if len(data):
            related_queryset.set(data)

    @staticmethod
    def handle_one2m_field(data, instance, field):
        if not data:
            return None
        assert isinstance(data, (tuple, list)), "`data` should be a list or tuple."
        related_queryset = getattr(instance, field.related_name, None)
        existing_ids = list(related_queryset.values_list(field.unique_identifier, flat=True))
        for datum in data:
            if datum.get(field.unique_identifier):
                if issubclass(datum[field.unique_identifier].__class__, Model):
                    identifier_value = datum[field.unique_identifier].id
                else:
                    identifier_value = datum[field.unique_identifier]
                try:
                    related_instance = related_queryset.get(**{field.unique_identifier: identifier_value})
                    field.serializer(partial=True).update(related_instance, datum)
                    try:
                        existing_ids.remove(identifier_value)
                    except (KeyError, ValueError):
                        pass
                except ObjectDoesNotExist:
                    datum[field.parent_name] = instance
                    field.serializer().create(datum)
            else:
                datum[field.parent_name] = instance
                field.serializer().create(datum)
            # Delete objects with existing_ids
        for existing_id in existing_ids:
            related_queryset.get(**{field.unique_identifier: existing_id}).delete()

    @staticmethod
    def handle_one2m_generic_field(data, instance, field):
        if not data:
            return None
        assert isinstance(data, (tuple, list)), "`data` should be a list or tuple."
        related_queryset = getattr(instance, field.related_name, None)
        existing_ids = list(related_queryset.values_list(field.unique_identifier, flat=True))
        for datum in data:
            if datum.get(field.unique_identifier):
                if issubclass(datum[field.unique_identifier].__class__, Model):
                    identifier_value = datum[field.unique_identifier].id
                else:
                    identifier_value = datum[field.unique_identifier]
                try:
                    related_instance = related_queryset.get(**{field.unique_identifier: identifier_value})
                    field.serializer(partial=True).update(related_instance, datum)
                    try:
                        existing_ids.remove(identifier_value)
                    except (KeyError, ValueError):
                        pass
                except ObjectDoesNotExist:
                    datum[field.generic_foreign_key_field] = instance
                    field.serializer().create(datum)
            else:
                datum[field.generic_foreign_key_field] = instance
                field.serializer().create(datum)
        # Delete objects with existing_ids
        for existing_id in existing_ids:
            related_queryset.get(**{field.unique_identifier: existing_id}).delete()

    def handle_related_object(self, field, data, instance=None):
        if not hasattr(field, "related_name") or not field.related_name:
            field.related_name = field.field_name

        if isinstance(field, ForeignKeyField) or isinstance(field, URLField):
            return {field.attribute_name: data}
        elif isinstance(field, OneToOneField) and field.execute_first:
            if self.partial:
                related_instance = getattr(instance, field.related_name)
                field.serializer(partial=True).update(related_instance, data)
                return {}
            else:
                return {field.related_name: field.serializer().create(data)}
        elif isinstance(field, OneToOneField):
            self.one2one_fields[field] = data
            return {}
        elif isinstance(field, OneToManyField):
            self.one2m_fields[field] = data
            return {}
        elif isinstance(field, OneToManyGenericField):
            self.one2m_generic_fields[field] = data
            return {}
        elif isinstance(field, ManyToManyField):
            self.m2m_fields[field] = data
            return {}
        else:
            return {}

    def segregate_data(self, validated_data, instance=None):
        cleaned_validated_data = OrderedDict()
        for field_name, value in validated_data.items():
            field = self.fields.get(field_name)
            if issubclass(field.__class__, DjangoRelatedField) or isinstance(field, URLField) \
                    or isinstance(field, ForeignKeyField):
                cleaned_validated_data.update(self.handle_related_object(field, value, instance))
            else:
                cleaned_validated_data[field_name] = value
        return cleaned_validated_data

    def upsert_related_objects(self, instance):
        # Create One to One objects
        for field, value in self.one2one_fields.items():
            self.handle_one_to_one_field(value, instance=instance, field=field)
        # Create Many to Many objects
        for field, value in self.m2m_fields.items():
            self.handle_m2m_field(data=value, instance=instance, field=field)
        # Create One to Many objects
        for field, value in self.one2m_fields.items():
            self.handle_one2m_field(data=value, instance=instance, field=field)
        # Create One to Many Generic Related Fields
        for field, value in self.one2m_generic_fields.items():
            self.handle_one2m_generic_field(data=value, instance=instance, field=field)

    def create(self, validated_data):
        cleaned_validated_data = self.segregate_data(validated_data)
        # Destruct the obsolete validated_data
        del validated_data
        # Call create() containing only flat fields
        instance = super().create(cleaned_validated_data)
        self.upsert_related_objects(instance)
        return instance

    def update(self, instance, validated_data):
        cleaned_validated_data = self.segregate_data(validated_data, instance)
        del validated_data
        instance = super().update(instance, cleaned_validated_data)
        self.upsert_related_objects(instance)
        return instance

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, dict):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            })

        ret = OrderedDict()
        errors = OrderedDict()
        fields = self._writable_fields

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            field.partial = self.partial
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = list(exc.messages)
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        return ret