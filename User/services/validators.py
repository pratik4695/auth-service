import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email, RegexValidator
from django.utils.deconstruct import deconstructible

from User.constants import MOBILE_NUMBER_REGEX
from User.models import User
from core.exceptions import InvalidMobileNumber
from utils import encdec


@deconstructible
class MobileValidator:
    validator_all_digits = RegexValidator(regex='^\d+$', message='In Phone number only numeric value are allowed.')
    validator_mobile = RegexValidator(regex=MOBILE_NUMBER_REGEX, message='Please enter a valid 10 digit Phone number')

    default_message = "Please enter a 10 digit Phone number"

    def __init__(self, raise_specific_error=False):
        self.raise_specific_error = raise_specific_error

    def __call__(self, value):
        try:
            self.validator_all_digits(value)
            self.validator_mobile(value)
        except ValidationError as ve:
            raise InvalidMobileNumber(ve.message) if self.raise_specific_error else ValidationError(
                self.default_message)

    def __eq__(self, other):
        return self.raise_specific_error == other.raise_specific_error


mobile_validator = MobileValidator()
mobile_validator_with_specific_error = MobileValidator(raise_specific_error=True)


def email_or_mobile_validator(value):
    """
    Created by Amrullah on 20/10/2015
    """
    if '@' in value:
        validate_email(value)
    elif re.match('^\d+$', value):
        mobile_validator(value)
    else:
        raise ValidationError("Please enter a valid email or phone number")


def user_type_validator(value):
    if value not in User.get_user_types_list():
        raise ValidationError('Improper user_type %s' % value)


def decrypt_user_from_encryption(mobile_encrypted, email_encrypted):
    mobile = encdec.DecodeAES(mobile_encrypted)
    email_decoded = encdec.DecodeAES(email_encrypted)
    email = User.get_non_temp_email(email_decoded)
    return mobile, email
