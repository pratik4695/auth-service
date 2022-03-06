import uuid

import jwt
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from random import randint
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.core.validators import RegexValidator, validate_email
from django.db import models, transaction
from django.utils import timezone
from model_utils.models import TimeStampedModel, MonitorField

from User.constants import RAW_PASSWORD, MOBILE_NUMBER_REGEX, UserAccessCodeType, GenderChoices, UserTypes, \
    LanguageChoices, UserHistoryActions
from User.helpers.user import validate_password
from User.models.manager import UserManager
from core.grpc_exceptions import ValidationError
from core.validators import user_json_validator, validate_for_ascii_chars, age_validator

# from utils import encdec
from utils import encdec


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
        Custom user model
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = None
    email_hash = models.CharField(max_length=255, db_index=False)
    email_encrypted = models.CharField(max_length=255, db_index=False)
    # email_last_updated_on = MonitorField(monitor='email_hash', null=True, default=None)
    mobile = None
    mobile_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    mobile_encrypted = models.CharField(max_length=255, null=True, blank=True, db_index=False)
    # mobile_last_updated_on = MonitorField(monitor='mobile_hash', null=True, default=None)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True, validators=[age_validator])
    # photo = models.ImageField(max_length=255, upload_to=get_upload_file_name, blank=True, null=True, default=None)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, blank=True, null=True,
                              validators=[GenderChoices.validator])
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True)
    deleted_by = models.ForeignKey('self', null=True, blank=True, default=None, related_name='deleted_users',
                                   on_delete=models.PROTECT)
    user_type = models.CharField(max_length=5, choices=UserTypes.choices, validators=[UserTypes.validator],
                                 default=UserTypes.PERMANENT)
    is_admin = models.BooleanField(default=False)
    email_subscribed = models.BooleanField(default=True, verbose_name="Transactional email setting")
    sms_subscribed = models.BooleanField(default=True, verbose_name="Transactional sms setting")
    whatsapp_subscribed = models.BooleanField(null=True, verbose_name="Transactional/Marketing whatsapp setting")

    preferred_language = models.CharField(max_length=2, choices=LanguageChoices.choices,
                                          default=LanguageChoices.ENGLISH, validators=[LanguageChoices.validator])
    mobile_verified = models.BooleanField(default=False)
    mobile_verified_on = MonitorField(monitor='mobile_verified', when=[True], null=True, blank=True, default=None)
    email_verified = models.BooleanField(default=False)
    email_verified_on = MonitorField(monitor='email_verified', when=[True], null=True, blank=True, default=None)
    # to identify, whether user is having actual email or not
    email_exists = models.BooleanField(default=True)
    last_visit = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # Boolean to check whether the user has set password or not
    password_exists = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['mobile_hash', 'email_hash']
    # some extra properties. to be initialized at the time class is loaded
    mobile_validator = RegexValidator(regex=MOBILE_NUMBER_REGEX)

    AVOID_PATTERN_INDEX_FOR = ("email_hash", "email_encrypted", "mobile_hash", "mobile_encrypted", "user_type")

    def __check_mobile_number_existence(self, mobile):
        if User.objects.exclude(id=self.id).filter(mobile=mobile).exists():
            raise ValidationError(
                "This given mobile number is already associated with some different user.")
            # raise CustomValidationError("Mobile number {0} is already registered".format(mobile))

    def __init__(self, *args, **kwargs):
        """
        Custom init method, need arose primarily because email and mobile has to be converted to
        email_hash, email_encrypted and mobile_hash and mobile_encrypted respectively.
        :param args:
        :param kwargs:
        :return:
        """
        mobile = kwargs.pop('mobile', None)
        email = kwargs.pop('email', None)
        super().__init__(*args, **kwargs)

        if mobile:
            self._set_mobile(mobile, auto_save=False)
        if email:
            self._set_email(email, auto_save=False)

    def _set_mobile(self, mobile, auto_save=False):
        """
        :param mobile:
        This method is not thread-safe for mobile_hash (Ideally, DB lock should be acquired while setting mobile number).
        There is a probability (very low though) that two threads could be setting the same mobile at same time, and no error would be thrown since
        there is no unique constraint on mobile_hash.
        :auto_save: to check whether to save mobile number or not
        """
        try:
            mobile = mobile.strip() if (mobile and mobile.strip()) else None
            self.mobile_validator(mobile)
        except ValidationError:
            raise ValidationError("Invalid mobile number provided, expected {0}".format(MOBILE_NUMBER_REGEX))
        else:
            self.__check_mobile_number_existence(mobile)
            self.mobile_hash = encdec.Hash(mobile)
            self.mobile_encrypted = encdec.EncodeAES(mobile)
            update_fields = ["mobile_hash", "mobile_encrypted", "modified"]

            if auto_save:
                self.save(update_fields=update_fields)
        return mobile

    @staticmethod
    def lower_case_email(email):
        if email:
            email = email.strip()
            email = email.lower()
        return email

    def _set_email(self, email, auto_save=False):
        """
        :param email:
        """
        email = self.lower_case_email(email)
        validate_email(email)
        validate_for_ascii_chars(email)
        # not handled the reverse case; Case: when user remove existing email ID
        self.email_hash = encdec.Hash(email)
        self.email_encrypted = encdec.EncodeAES(email)
        if auto_save:
            self.save(update_fields=["email_hash", "email_encrypted", "modified"])
        return email

    def decrypt_email(self):
        """
        Decrypt email
        """
        if self.email_encrypted is not None:
            self.email = encdec.DecodeAES(self.email_encrypted)
        else:
            self.email = None

    def decrypt_mobile(self):
        """
        Decrypt mobile
        """
        if self.mobile_encrypted is not None:
            self.mobile = encdec.DecodeAES(self.mobile_encrypted)
        else:
            self.mobile = None

    def decrypt_data(self):
        """
        Decrypt all info in user instance
        """
        self.decrypt_email()
        self.decrypt_mobile()

    @property
    def name(self):
        """
        Returns Full Name of the User
        :return: first_name + ' ' + last_name
        """
        return self.get_full_name()

    def get_full_name(self):
        """
        Returns Full Name of the User
        :return: first_name + ' ' + last_name
        """
        name_components = [_ for _ in [self.first_name, self.last_name] if _]
        return " ".join(name_components)

    # def _set_password(self, raw_password=None):
    #     if raw_password is None:
    #         raw_password = RAW_PASSWORD
    #     else:
    #         validate_password(raw_password)
    #     super().set_password(raw_password)

    def _set_password(self, raw_password):
        if raw_password is None:
            self.password_exists = False
        else:
            self.password_exists = True
        super().set_password(raw_password)

    @transaction.atomic
    def soft_delete(self, deleted_by):
        # soft delete
        self.is_deleted = True
        self.deleted_by = deleted_by
        self.deleted_on = datetime.now()
        self.is_active = False
        self.save(update_fields=['is_deleted', 'deleted_by', 'deleted_on', 'is_active'])

    @transaction.atomic
    def reactivate_user(self):
        self.is_deleted = False
        self.deleted_by = None
        self.deleted_on = None
        self.is_active = True
        self.save(update_fields=['is_deleted', 'deleted_by', 'deleted_on', 'is_active'])

    @transaction.atomic
    def activate_user(self, modified_by, comment=None):
        self.is_active = True
        self.save(update_fields=["is_active"])

    def _set_email_verified(self, code_status):
        """
        setting email verified from here, if email get verified. Trigger the required event from here
        :param code_status: True/False
        :return:
        """
        if not self.email_verified and code_status:
            self.email_verified = True
            self.save(update_fields=["email_verified", "email_verified_on", "is_active"])

        return code_status

    def set_email_unverified(self, auto_save=True, modified_by=None, comment=None):
        if not self.email_verified:
            return False
        self.email_verified = False
        self.email_verified_on = None
        self.create_history(action=UserHistoryActions.EMAIL_UNVERIFIED, modified_by=modified_by, comment=comment)
        if auto_save:
            self.save(update_fields=["email_verified", "email_verified_on"])
        return True

    def set_mobile_unverified(self, auto_save=True, modified_by=None, comment=None):
        if not self.mobile_verified:
            return False
        self.mobile_verified = False
        self.mobile_verified_on = None
        self.verified_by = None
        self.create_history(action=UserHistoryActions.MOBILE_UNVERIFIED, modified_by=modified_by, comment=comment)
        if auto_save:
            self.save(update_fields=["mobile_verified", "mobile_verified_on", "is_active", "verified_by"])
        return True

    def _set_mobile_verified(self, otp_status, verified_by=None):
        if not self.mobile_verified and otp_status:
            self.mobile_verified = True
            update_fields = ["mobile_verified", "mobile_verified_on", "is_active", "verified_by"]
            self.save(update_fields=update_fields)

        return otp_status

    def create_history(self, action, pre_value=None, post_value=None, modified_by=None, comment=None):
        from User.models import UserHistory
        UserHistory.objects.create(user=self, pre_value=pre_value, post_value=post_value, modified_by=modified_by,
                                   action=action, comment=comment)

    @property
    def jwt(self):
        try:
            dt = datetime.now() + timedelta(days=60)
            payload = {
                "id": str(self.id),
                "name": self.name,
                "user_type": self.user_type,
                "expires": str(dt)
            }
            return jwt.encode(payload, settings.ENCRYPT_KEY, algorithm="HS256").decode()
        except Exception as ex:
            print("Failed to fetch JWT token for user {}, reason: {}".format(self.id, ex))
            return None

    @property
    def age(self):
        """
        Gives age of the User using data of birth
        :return: Age in integers
        """
        if self.date_of_birth is not None:
            return relativedelta(date.today(), self.date_of_birth).years
        else:
            return None

    # def _check_and_set_is_active(self):
    #     """
    #     if user is not active, then check whether email or mobile is verified or not
    #     :return: Nothing
    #     """
    #     if not self.is_active and (self.email_verified or self.mobile_verified):
    #         self.is_active = True

    @property
    def is_staff(self):
        return self.is_admin

    # def save(self, *args, **kwargs):
    #     self._check_and_set_is_active()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.name or ("Id:" + str(self.id))

    def get_short_name(self):
        """
        Returns first_name of the User
        :return: first_name
        """
        return self.first_name

    def set_password_with_history(self, raw_password, modified_by=None, comment=None):
        self._set_password(raw_password)
        self.create_history(action=UserHistoryActions.PASSWORD_CHANGED, modified_by=modified_by, comment=comment)

    # def set_photo(self, photo_url, auto_save=True):
    #     # Strip AWS S3 Custom Domain
    #     if photo_url is not None:
    #         custom_domain = default_storage.url(name='')
    #         photo_url = photo_url.replace(custom_domain, "")
    #         self.photo = photo_url
    #         if auto_save:
    #             self.save(update_fields=['photo', 'modified'])

    def set_email_verified_with_history(self, code_status, modified_by=None, comment=None):
        if not self.email_verified and code_status:
            self._set_email_verified(code_status)
            self.create_history(action=UserHistoryActions.EMAIL_VERIFIED, modified_by=modified_by, comment=comment)

        return code_status

    @transaction.atomic
    def set_mobile_verified_with_history(self, otp_status, modified_by=None, comment=None):
        if not self.mobile_verified and otp_status:
            self._set_mobile_verified(otp_status, verified_by=modified_by)
            self.create_history(action=UserHistoryActions.MOBILE_VERIFIED, modified_by=modified_by, comment=comment)

        return otp_status

    def generate_and_send_otp(self, reset_code_type, otp_via_email=False):
        """
        can generate the activation code according to activation mode
        :param reset_code_type: Code for mobile: M ; For Email: E, For login : L, For Access code: AC
        :param otp_via_email: Send OTP via email
        :return: generated code
        """
        otp = None
        if reset_code_type == UserAccessCodeType.ACTIVATION_CODE:
            otp = self.reset_code.generate_activation_otp()
        elif reset_code_type == UserAccessCodeType.LOGIN_CODE:
            otp = self.reset_code.generate_login_otp()
        elif reset_code_type == UserAccessCodeType.PASSWORD_RESET_CODE:
            otp = self.reset_code.generate_password_otp()
        elif reset_code_type == UserAccessCodeType.PROFILE_ACCESS_CODE:
            otp = self.reset_code.generate_access_otp()
        elif reset_code_type == UserAccessCodeType.EMAIL_ACTIVATION_CODE:
            otp = self.reset_code.generate_activation_otp()
        #
        if otp is not None:
            self.send_otp(otp, reset_code_type, otp_via_email=otp_via_email)
            return True
        else:
            raise ValidationError("Reset code type is missing/Invalid")

    def generate_and_send_code(self, form_url, reset_code_type):
        hash_code = None
        if reset_code_type == UserAccessCodeType.ACTIVATION_CODE:
            hash_code = self.reset_code.generate_email_code()
        elif reset_code_type == UserAccessCodeType.PASSWORD_RESET_CODE:
            hash_code = self.reset_code.generate_password_reset_code()
        elif reset_code_type == UserAccessCodeType.SET_PASSWORD_CODE:
            hash_code = self.reset_code.generate_password_reset_code()
        #
        if hash_code is not None:
            self.send_code(hash_code, form_url, reset_code_type)
            return True
        else:
            raise ValidationError("Reset code type is missing/Invalid")

    def validate_code(self, hash_code, reset_code_type, modified_by=None):
        code_status = None
        if reset_code_type == UserAccessCodeType.ACTIVATION_CODE:
            code_status = self.reset_code.validate_activation_code(hash_code)
            self.reset_temporary_email(code_status, modified_by=modified_by)
        elif reset_code_type == UserAccessCodeType.PASSWORD_RESET_CODE:
            code_status = self.reset_code.validate_password_code(hash_code)
        elif reset_code_type == UserAccessCodeType.SET_PASSWORD_CODE:
            code_status = self.reset_code.validate_password_code(hash_code)
        elif reset_code_type == UserAccessCodeType.ALL_CODES:
            code_status = self.reset_code.validate_activation_code(hash_code) or \
                          self.reset_code.validate_password_code(hash_code)
        #
        if code_status is not None:
            return self.set_email_verified_with_history(code_status, modified_by=modified_by,
                                                        comment="Actioned from validate code; type:{0},"
                                                                " code: {1}".format(reset_code_type, hash_code))
        else:
            return False

    def validate_otp(self, otp, reset_code_type, modified_by=None):
        otp_status = None
        if reset_code_type == UserAccessCodeType.ACTIVATION_CODE:
            otp_status = self.reset_code.validate_activation_otp(otp)
        elif reset_code_type == UserAccessCodeType.LOGIN_CODE:
            otp_status = self.reset_code.validate_login_otp(otp)
        elif reset_code_type == UserAccessCodeType.PASSWORD_RESET_CODE:
            otp_status = self.reset_code.validate_password_otp(otp)
        elif reset_code_type == UserAccessCodeType.PROFILE_ACCESS_CODE:
            otp_status = self.reset_code.validate_access_otp(otp)
        elif reset_code_type == UserAccessCodeType.EMAIL_ACTIVATION_CODE:
            otp_status = self.reset_code.validate_activation_otp(otp)
        #
        if otp_status is not None:
            if reset_code_type == UserAccessCodeType.EMAIL_ACTIVATION_CODE:
                return self.set_email_verified_with_history(otp_status, modified_by=modified_by,
                                                            comment="Actioned from validate otp; "
                                                                    "type:{0}, otp:{1}".format(reset_code_type, otp))
            else:
                return self.set_mobile_verified_with_history(otp_status, modified_by=modified_by,
                                                             comment="Actioned from validate otp; "
                                                                     "type:{0}, otp:{1}".format(reset_code_type, otp))
        else:
            return False

    # def validate_auto_login_code(self, hash_code, code_type, modified_by=None):
    #     reset_code = False
    #     if code_type == "mobile":
    #         login_code_status = self.login_codes.filter(code=hash_code, expiry__gte=datetime.now(),
    #                                                     code_type=LoginCodeTypes.sms).exists()
    #         reset_code = self.set_mobile_verified_with_history(login_code_status, modified_by=modified_by,
    #                                                            comment="Actioned from validate_auto_login_code;"
    #                                                                    " type:{0}, hash_code:{1}".format(code_type,
    #                                                                                                      hash_code))
    #     elif code_type == "email":
    #         reset_code = self.validate_code(hash_code, reset_code_type=UserAccessCodeType.ALL_CODES)
    #         if not reset_code:
    #             login_code_status = self.login_codes.filter(code=hash_code, expiry__gte=datetime.now(),
    #                                                         code_type=LoginCodeTypes.email).exists()
    #             reset_code = self.set_email_verified_with_history(login_code_status, modified_by=modified_by,
    #                                                               comment="Actioned from validate_auto_login_code;"
    #                                                                       " type:{0}, hash_code:{1}".format(code_type,
    #                                                                                                         hash_code))
    #     return reset_code

    # def send_otp(self, otp, reset_code_type, otp_via_email=False):
    #
    #     self.decrypt_data()
    #     if otp_via_email:
    #         if reset_code_type in [UserAccessCodeType.ACTIVATION_CODE, UserAccessCodeType.EMAIL_ACTIVATION_CODE]:
    #             send_to = self.reset_code.temp_email if self.email_verified \
    #                                                     and self.reset_code.temp_email else self.email
    #         else:
    #             send_to = self.email
    #         # transaction.on_commit(EmailOtpService(user=self, otp=otp, reset_code_type=reset_code_type))
    #     else:
    #         send_to = self.reset_code.temp_mobile if self.mobile_verified \
    #                                                  and self.reset_code.temp_mobile else self.mobile
    #         if reset_code_type == UserAccessCodeType.ACTIVATION_CODE:
    #             ResendActivationCode(user=self, otp=otp, send_to=send_to).__call__()
    #             if self.mobile and self.reset_code.temp_mobile == send_to and self.email_verified:
    #                 from authentication.utils import get_password_reset_url
    #                 handlebars_data = {
    #                     "new_mobile": send_to,
    #                     "first_name": self.first_name,
    #                     "made_changes_url": settings.OLX_JOBS_RECRUIT_WEBSITE,
    #                     "did_not_made_changes_url": get_password_reset_url(self)
    #                 }
    #
    #                 MobileChangeNotificationOnVerifiedEmail(self, handlebars_data).__call__()
    #         elif reset_code_type == UserAccessCodeType.LOGIN_CODE:
    #             SendLoginOTP(user=self, otp=otp, send_to=send_to).__call__()
    #
    #         elif reset_code_type == UserAccessCodeType.PASSWORD_RESET_CODE:
    #             PasswordResetCode(user=self, otp=otp, send_to=send_to).__call__()
    #
    #         elif reset_code_type == UserAccessCodeType.PROFILE_ACCESS_CODE:
    #             UserAccessCode(user=self, otp=otp, send_to=send_to).__call__()
    #
    #         else:
    #             send_to = self.mobile
    #             # transaction.on_commit(lambda: send_sms_to_user.apply_async((self, send_to,
    #             #                                                             otp, reset_code_type, None, aj_client),
    #             #                                                            countdown=2))
    #             from notifications.tasks.common.otp_sms import SendOTP
    #             transaction.on_commit(SendOTP(user=self, send_to=send_to, otp=otp, reset_code_type=reset_code_type))

    # def send_code(self, hash_code, form_url, reset_code_type):
    #     self.decrypt_email()
    #     if reset_code_type == UserAccessCodeType.ACTIVATION_CODE:
    #         send_to = self.reset_code.temp_email if self.email_verified else self.email
    #     else:
    #         send_to = self.email
    #     if send_to is None:
    #         raise CustomValidationError("provided email is not valid. Please recheck!!")
    #     if self.email is None:
    #         raise CustomValidationError("User does not contain email ID!!!")
    #
    #     email_url = form_url + "?username=" + self.email + "&hash_code=" + hash_code
    #     if self.reset_code.temp_email and self.email_verified:
    #
    #         EmailChangeNotificationOnVerifiedEmail(self.id, email_url, send_to).__call__()
    #     transaction.on_commit(EmailVerificationService(self.id, email_url, reset_code_type, send_to))


class UserJWTToken(TimeStampedModel):
    """
        Keeping the Access and Refresh Token
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=400)
    refresh_token = models.CharField(max_length=400)
    expires = models.DateTimeField()

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        if not self.expires:
            return True

        return timezone.now() >= self.expires


class UserActivationKey(TimeStampedModel):
    """
    Will use this model for password reset, forgot password etc,
    send this reset code to mobile or email whichever is verified
    can include expiry time field in future
    """
    user = models.OneToOneField(User, related_name='reset_code', db_index=True, on_delete=models.CASCADE)

    activation_otp = models.CharField(max_length=5, null=True, blank=True)
    activation_otp_expiry = models.DateTimeField(null=True, blank=True)

    activation_code = models.CharField(max_length=255, null=True, blank=True)
    activation_code_expiry = models.DateTimeField(null=True, blank=True)

    login_otp = models.CharField(max_length=255, null=True, blank=True)
    login_otp_expiry = models.DateTimeField(null=True, blank=True)

    password_otp = models.CharField(max_length=255, null=True, blank=True)
    password_otp_expiry = models.DateTimeField(null=True, blank=True)

    access_otp = models.CharField(max_length=255, null=True, blank=True)
    access_otp_expiry = models.DateTimeField(null=True, blank=True)

    password_reset_code = models.CharField(max_length=255, null=True, blank=True)
    password_reset_code_expiry = models.DateTimeField(null=True, blank=True)

    temp_email = models.CharField(max_length=100, null=True, blank=True)
    temp_mobile = models.CharField(max_length=11, null=True, blank=True)

    def generate_otp(self):
        self.user.decrypt_mobile()
        if self.user.mobile == settings.TEST_MOBILE:
            otp_code = str(settings.TEST_LOGIN_OTP)
            return otp_code
        opt_code = str(randint(10000, 99999))
        return opt_code

    # *********************** Generate reset code/OTP *******************************

    def generate_login_otp(self, hard_generate=False):
        if self.login_otp_expiry and self.login_otp_expiry > timezone.now() and self.login_otp and not hard_generate:
            return self.login_otp
        else:
            login_otp = self.generate_otp()
            self.login_otp = login_otp
            self.login_otp_expiry = datetime.now() + timedelta(minutes=15)
            self.save(update_fields=['login_otp', 'login_otp_expiry'])
            return login_otp

    def generate_activation_otp(self, hard_generate=False):
        if self.activation_otp_expiry and self.activation_otp_expiry > timezone.now() and self.activation_otp and \
                not hard_generate:
            return self.activation_otp
        else:
            generated_otp = self.generate_otp()
            self.activation_otp = generated_otp
            self.activation_otp_expiry = datetime.now() + timedelta(minutes=15)
            self.save(update_fields=['activation_otp', 'activation_otp_expiry'])
            return generated_otp

    def generate_email_code(self, hard_generate=False):
        if self.activation_code_expiry and self.activation_code_expiry > timezone.now() and self.activation_code and \
                not hard_generate:
            return self.activation_code
        else:
            email_reset_code = self.generate_otp()
            hash_code = encdec.Hash(self.user.email_hash + email_reset_code)
            print(hash_code)
            self.activation_code = hash_code
            self.activation_code_expiry = datetime.now() + timedelta(days=1)
            self.save(update_fields=['activation_code', 'activation_code_expiry'])
            return hash_code

    def generate_access_otp(self, hard_generate=False):
        if self.access_otp_expiry and self.access_otp_expiry > timezone.now() and self.access_otp and not hard_generate:
            return self.access_otp
        else:
            access_otp = self.generate_otp()
            self.access_otp = access_otp
            self.access_otp_expiry = datetime.now() + timedelta(seconds=890)
            self.save(update_fields=['access_otp', 'access_otp_expiry'])
            return access_otp

    def generate_password_otp(self, hard_generate=False):
        if self.password_otp_expiry and self.password_otp_expiry > timezone.now() and self.password_otp \
                and not hard_generate:
            return self.password_otp
        else:
            password_otp = self.generate_otp()
            self.password_otp = password_otp
            self.password_otp_expiry = datetime.now() + timedelta(minutes=15)
            self.save(update_fields=['password_otp', 'password_otp_expiry'])
            return password_otp

    def generate_password_reset_code(self, hard_generate=False):
        if self.password_reset_code_expiry and self.password_reset_code_expiry > timezone.now() and \
                self.password_reset_code and not hard_generate:
            return self.password_reset_code
        else:
            password_code = self.generate_otp()
            hash_code = encdec.Hash(self.user.email_hash + password_code)
            self.password_reset_code = hash_code
            self.password_reset_code_expiry = datetime.now() + timedelta(days=2)
            self.save(update_fields=['password_reset_code', 'password_reset_code_expiry'])
            return hash_code

    # *************************************** Validate OTP/ reset code *******************************

    def validate_activation_otp(self, otp):
        if self.activation_otp_expiry and self.activation_otp_expiry > timezone.now() and self.activation_otp == otp:
            self.generate_activation_otp(hard_generate=True)
            return True
        else:
            return False

    def validate_login_otp(self, otp):
        if self.login_otp_expiry and self.login_otp_expiry > timezone.now() and self.login_otp == otp:
            self.generate_login_otp(hard_generate=True)
            return True
        else:
            return False

    def validate_access_otp(self, otp):
        if self.access_otp_expiry and self.access_otp_expiry > timezone.now() and self.access_otp == otp:
            self.generate_access_otp(hard_generate=True)
            return True
        else:
            return False

    def validate_password_otp(self, otp):
        if self.password_otp_expiry and self.password_otp_expiry > timezone.now() and self.password_otp == otp:
            self.generate_password_otp(hard_generate=True)
            return True
        else:
            return False

    def validate_activation_code(self, hash_code):
        if self.activation_code_expiry and self.activation_code_expiry > timezone.now() and self.activation_code == hash_code:
            self.generate_email_code(hard_generate=True)
            return True
        else:
            return False

    def validate_password_code(self, hash_code):
        if self.password_reset_code_expiry and self.password_reset_code_expiry > timezone.now() and self.password_reset_code == hash_code:
            self.generate_password_reset_code(hard_generate=True)
            return True
        else:
            return False

    def __str__(self):
        return self.user.name + "'s codes"
