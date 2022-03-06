from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

from core.constants import MOBILE_NUMBER_REGEX
from core.exceptions import InvalidMobileNumber


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


def user_json_validator(value):
    if not isinstance(value, dict):
        raise ValidationError("Expected dict, {} provided".format(type(value)))
    _allowed_fields = (
        "id", "first_name", "last_name", "name", "user_type", "entity_id", "platform", "employee_id", "mobile")
    for key in value.keys():
        if key not in _allowed_fields:
            raise ValidationError("Invalid identifier {} in value".format(key))


def user_role_json_validator(value):
    if not isinstance(value, dict):
        raise ValidationError("Expected dict, {} provided".format(type(value)))
    _allowed_fields = ("id", "name")
    for key in value.keys():
        if key not in _allowed_fields:
            raise ValidationError("Invalid identifier {} in value".format(key))


def notify_json_validator(value):
    if not isinstance(value, dict):
        raise ValidationError("Expected dict, {} provided".format(type(value)))
    _allowed_fields = ("value", "unit")
    for key in value.keys():
        if key not in _allowed_fields:
            raise ValidationError("Invalid identifier {} in value".format(key))


def validate_for_ascii_chars(value):
    try:
        assert isinstance(value, str), "Should be string, got %s" % type(value)
        value.encode('ascii')
    except AssertionError:
        raise ValidationError("value should be a string")


def validate_for_numeric_chars(value):
    if not value.isdecimal():
        raise ValidationError("value should be a number")


def organization_holiday_date_validator(value):
    if not isinstance(value, dict):
        raise ValidationError("Expected dict, {} provided".format(type(value)))


def age_validator(value):
    """
    This function validates age of candidate with restriction as, date of birth can't be a future date, and also
    age can't be less that 14 years (Legal working age in India)
    :param value: Instance of DateField
    """
    if value > date.today():
        raise ValidationError("Date of Birth can't be in future if you are not a time-traveller!")
    if relativedelta(date.today(), value).years < 14:
        raise ValidationError("Minimum Legal Working Age in India is 14 years!")
