from django.contrib.auth.base_user import BaseUserManager
from django.db.models.query import QuerySet

from utils import encdec


def lower_case_email(email):
    if email:
        email = email.strip()
        email = email.lower()
    return email


def _update_args(*args):
    args_new = list(args)
    if 'mobile' in args:
        args_new.remove('mobile')
        args_new.extend(['mobile_hash', 'mobile_encrypted'])
    if 'email' in args:
        args_new.remove('email')
        args_new.extend(['email_hash', 'email_encrypted'])

    return args_new


def _update_search_params(**kwargs):
    keys = kwargs.keys()
    if 'mobile' in keys:
        mobile = kwargs.pop('mobile')
        kwargs['mobile_hash'] = encdec.Hash(mobile)
        kwargs['mobile_encrypted'] = encdec.EncodeAES(mobile)
    if 'email' in keys:
        email = lower_case_email(kwargs.pop('email'))
        kwargs['email_hash'] = encdec.Hash(email)
        kwargs['email_encrypted'] = encdec.EncodeAES(email)
    return kwargs


class CustomQuerySet(QuerySet):

    def aggregate(self, *args, **kwargs):
        kwargs = _update_search_params(**kwargs)
        return super().aggregate(*args, **kwargs)

    # def bulk_create(self, objs, batch_size=None):
    #     raise NotImplementedError("bulk_create on User model is not implemented. Cannot be called")

    def _values(self, *fields):
        fields = _update_args(*fields)
        return super()._values(*fields)

    def values_list(self, *fields, **kwargs):
        fields = _update_args(*fields)
        kwargs = _update_search_params(**kwargs)
        return super().values_list(*fields, **kwargs)

    def filter(self, *args, **kwargs):
        args = _update_args(*args)
        kwargs = _update_search_params(**kwargs)
        return super().filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        args = _update_args(*args)
        kwargs = _update_search_params(**kwargs)
        return super().exclude(*args, **kwargs)

    def select_related(self, *fields):
        fields = _update_args(*fields)
        return super().select_related(*fields)

    def order_by(self, *field_names):
        field_names = _update_args(*field_names)
        return super().order_by(*field_names)

    def distinct(self, *field_names):
        field_names = _update_args(*field_names)
        return super().distinct(*field_names)

    def defer(self, *fields):
        fields = _update_args(*fields)
        return super().defer(*fields)

    def only(self, *fields):
        fields = _update_args(*fields)
        return super().only(*fields)

    def in_bulk(self, id_list=None, *, field_name='pk'):
        new_id_list = map(encdec.Hash, id_list)
        return super().in_bulk(new_id_list)

    def get_or_create(self, defaults=None, **kwargs):
        kwargs = _update_search_params(**kwargs)
        return super().get_or_create(defaults, **kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        kwargs = _update_search_params(**kwargs)
        return super().update_or_create(defaults, **kwargs)

    def update(self, **kwargs):
        kwargs = _update_search_params(**kwargs)
        return super().update(**kwargs)

    def delete(self):
        assert not self.filter(groups__name='non_deletable_user').exists(), (
            "Some users can't be deleted as these belong to non-deletable group")
        return super().delete()

    @property
    def random_password(self):
        from random import choice
        from string import ascii_letters
        password = (''.join(choice(ascii_letters) for _ in range(6)))
        return password


class EmployeeManager(BaseUserManager):
    """
        This class is necessary to create if using custom user model is desired
    """
    def get_queryset(self):
        return CustomQuerySet(self.model, using=self._db)
