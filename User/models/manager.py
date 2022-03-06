from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist, ValidationError
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


class UserQuerySet(QuerySet):

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

    def in_bulk(self, id_list):
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

    def create(self, **kwargs):
        """
        overridden because we want to set some default values when instance is first created
        """
        # # Set random password at the time of creation
        # password_provided = True if kwargs.get("password") else False
        # if not password_provided:
        #     kwargs.update({
        #         "password": self.random_password,
        #         "password_exists": False
        #     })
        # #
        email = kwargs.get("email")
        email = email.strip() if (email and email.strip()) else None
        #
        mobile = kwargs.get("mobile")
        mobile = mobile.strip() if (mobile and mobile.strip()) else None
        #
        if not (email or kwargs.get("email_hash")):
            if not mobile:
                raise ValueError("Both email and mobile cannot be null")
        # ------------- Below code is copy and pasted from queryset, except for obj.set_password
        obj = self.model(**kwargs)
        obj._set_password(kwargs.get('password'))
        self._for_write = True
        obj.save(force_insert=True, using=self.db)

        return obj


class UserManager(BaseUserManager):
    """
        This class is necessary to create if using custom user model is desired
    """

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def create_user(self, email=None, mobile=None, password=None, is_active=None, **extra_fields):
        """
        :param email:
        :param mobile:
        :param password:
        :param extra_fields:
        :param is_active:
        :return:
        """
        # extra_fields.setdefault('is_admin', False)
        # extra_fields.setdefault('is_superuser', False)
        is_active = True if (extra_fields.get('uid', None) and is_active is None) else is_active
        return self._create_user(email=email, mobile=mobile, password=password, is_active=is_active, **extra_fields)

    def _create_user(self, email, mobile, password, is_active=None, **extra_fields):
        """
        :param email:
        :param is_active:
        :param mobile:
        :param password:
        :param extra_fields:
        :param is_active:
        :return: :raise ValueError:
        """
        if extra_fields.get('username'):
            raise ValueError('username can not be specified by User. Its generated Automatically')
        social_uid = extra_fields.pop('uid', None)
        email_verified = False
        if not email:
            if social_uid:
                # If the facebook user deselect to share email, then we store uid@facebook.com in User's email field
                email = social_uid + '@facebook.com'
            else:
                raise ValueError("not enough identification details")
        else:
            email_verified = True if social_uid else False

        # normalizing email like converting in lowercase
        normalized_email = UserManager.normalize_email(email)
        try:
            # user already exist, from this email id:
            user = self.get_queryset().get(email=normalized_email)
            return user
        except ObjectDoesNotExist:
            user = self.model(mobile=mobile, email=normalized_email, is_active=is_active, email_verified=email_verified,
                              **extra_fields)
            user._set_password(password)
            user.save(using=self._db)
            #
            return user

    def create_superuser(self, email=None, mobile=None, password=None, **extra_fields):
        """
        :param email:
        :param mobile:
        :param password:
        :param extra_fields:
        :return: :raise ValueError:
        """
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email=email, mobile=mobile, password=password, **extra_fields)
