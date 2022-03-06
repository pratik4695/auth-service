from djchoices import DjangoChoices, ChoiceItem
from django.utils.translation import gettext_lazy as _

RAW_PASSWORD = "rand0m@my123"

MOBILE_NUMBER_REGEX = "^[6-9]\d{9}$"


class AttendanceTabs(DjangoChoices):
    REPORT = ChoiceItem(value='REP', label=_("Report"))
    REQUEST = ChoiceItem(value='REQ', label=_("Request"))
    CONFIGURATION = ChoiceItem(value='CON', label=_("Configuration"))


class OrganizationTabs(DjangoChoices):
    USER_ROLES = ChoiceItem(value='USR', label=_("User Roles"))
    USER = ChoiceItem(value='US', label=_("User"))


class ObjectChoices(DjangoChoices):
    ANALYTICS = ChoiceItem(value='AN', label=_("Analytics"))
    PAYROLL = ChoiceItem(value='PA', label=_("Payroll"))
    COMPLIANCE = ChoiceItem(value='CO', label=_("Compliance"))
    EMPLOYEE = ChoiceItem(value='EM', label=_("Employee"))
    ANNOUNCEMENT = ChoiceItem(value='ANN', label=_("Announcement"))
    ATTENDANCE = ChoiceItem(value='AT', label=_("Attendance"))
    ORGANIZATION = ChoiceItem(value='OR', label=_("Organization"))
    ATT_REPORT = ChoiceItem(value='ATTREP', label=_("Report"))
    ATT_REQUEST = ChoiceItem(value='ATTREQ', label=_("Request"))
    ATT_CONFIGURATION = ChoiceItem(value='ATTCON', label=_("Configuration"))
    ORG_USER_ROLE = ChoiceItem(value='ORGUR', label=_("User Role"))
    ORG_USER = ChoiceItem(value='ORGU', label=_("User"))


class OperationChoices(DjangoChoices):
    CREATE = ChoiceItem(value='CR', label=_("Create"))
    UPDATE = ChoiceItem(value='UP', label=_("Update"))
    ALL = ChoiceItem(value='ALL', label=_("All"))
    READ = ChoiceItem(value='RE', label=_("Read"))


class ScopeChoices(DjangoChoices):
    ALL = ChoiceItem(value='ALL', label=_("All"))


class UserTypes(DjangoChoices):
    """
    To signify user_type field of User model
    """
    BETA = ChoiceItem(value='BT', label=_("Beta"))
    PERMANENT = ChoiceItem(value='PR', label=_("Permanent"))


class LanguageChoices(DjangoChoices):
    ENGLISH = ChoiceItem(value='en', label=_("English"))
    HINDI = ChoiceItem(value='hi', label=_("Hindi"))


class GenderChoices(DjangoChoices):
    MALE = ChoiceItem(value='M', label=_("Male"))
    FEMALE = ChoiceItem(value='F', label=_("Female"))


class LoginCodeTypes(DjangoChoices):
    EMAIL = ChoiceItem(value='E', label=_("Email"))
    SMS = ChoiceItem(value='S', label=_("Sms/Whatsapp"))


class UserAccessCodeType(DjangoChoices):
    ACTIVATION_CODE = ChoiceItem(value='A', label=_("Activation Code"))
    LOGIN_CODE = ChoiceItem(value='L', label=_("Login Code"))
    PASSWORD_RESET_CODE = ChoiceItem(value='P', label=_("Password Reset Code"))
    SET_PASSWORD_CODE = ChoiceItem(value='SP', label=_("Set Password Code"))
    PROFILE_ACCESS_CODE = ChoiceItem(value='AC', label=_("Profile Access Code"))
    EMAIL_ACTIVATION_CODE = ChoiceItem(value='EA', label=_("Email Activation Code"))
    ALL_CODES = ChoiceItem(value='ALL', label=_("All Code Types"))


class UserHistoryActions(DjangoChoices):
    MOBILE_ADDED = ChoiceItem(value='MOBILE_ADDED', label=_("New Mobile Added"))
    MOBILE_CHANGED = ChoiceItem(value='MOBILE_CHANGED', label=_("Mobile Changed"))
    MOBILE_VERIFIED = ChoiceItem(value='MOBILE_VERIFIED', label=_("Mobile Verified"))
    MOBILE_UNVERIFIED = ChoiceItem(value='MOBILE_UNVERIFIED', label=_("Mobile UnVerified"))
    MOBILE_NULL = ChoiceItem(value='MOBILE_NULL', label=_("Mobile Null"))
    MOBILE_DEAD = ChoiceItem(value='MOBILE_DEAD', label=_("Mobile Dead"))
    EMAIL_ADDED = ChoiceItem(value='EMAIL_ADDED', label=_("New Email Added"))
    EMAIL_CHANGED = ChoiceItem(value='EMAIL_CHANGED', label=_("Email Changed"))
    EMAIL_VERIFIED = ChoiceItem(value='EMAIL_VERIFIED', label=_("Email Verified"))
    EMAIL_UNVERIFIED = ChoiceItem(value='EMAIL_UNVERIFIED', label=_("Email UnVerified"))
    EMAIL_RANDOM = ChoiceItem(value='EMAIL_RANDOM', label=_("Random email set"))
    SMS_SUBSCRIBED = ChoiceItem(value='SMS_SUBSCRIBED', label=_("SMS Subscribed"))
    SMS_UNSUBSCRIBED = ChoiceItem(value='SMS_UNSUBSCRIBED', label=_("SMS Unsubcribed"))
    PROMO_SMS_SUBSCRIBED = ChoiceItem(value='PROMO_SMS_SUBSCRIBED', label=_("Promo SMS Subscribed"))
    PROMO_SMS_UNSUBSCRIBED = ChoiceItem(value='PROMO_SMS_UNSUBSCRIBED', label=_("Promo SMS Unsubcribed"))
    EMAIL_SUBSCRIBED = ChoiceItem(value='EMAIL_SUBSCRIBED', label=_("Email subscribed"))
    EMAIL_UNSUBSCRIBED = ChoiceItem(value='EMAIL_UNSUBSCRIBED', label=_("Email Unsubscribed"))
    PROMO_EMAIL_SUBSCRIBED = ChoiceItem(value='PROMO_EMAIL_SUBSCRIBED', label=_("Promo Email subscribed"))
    PROMO_EMAIL_UNSUBSCRIBED = ChoiceItem(value='PROMO_EMAIL_UNSUBSCRIBED', label=_("Promo Email Unsubscribed"))
    SYSTEM_EMAIL_SUBSCRIBED = ChoiceItem(value='SYSTEM_EMAIL_SUBSCRIBED', label=_("System Email subscribed"))
    SYSTEM_EMAIL_UNSUBSCRIBED = ChoiceItem(value='SYSTEM_EMAIL_UNSUBSCRIBED', label=_("System Email Unsubscribed"))
    ACTIVATED = ChoiceItem(value='ACTIVATED', label=_("User Activated"))
    DEACTIVATED = ChoiceItem(value='DEACTIVATED', label=_("User Deactivated"))
    REACTIVATED = ChoiceItem(value='REACTIVATED', label=_("User Reactivated"))
    PASSWORD_CHANGED = ChoiceItem(value='PASSWORD_CHANGED', label=_("Password Changed"))
    WHATSAPP_SUBSCRIBED = ChoiceItem(value='WHATSAPP_SUBSCRIBED', label=_("WhatsApp subscribed"))
    WHATSAPP_UNSUBSCRIBED = ChoiceItem(value='WHATSAPP_UNSUBSCRIBED', label=_("WhatsApp Unsubscribed"))
    WHATSAPP_SUBSCRIBED_FAILED = ChoiceItem(value='WHATSAPP_SUBSCRIBED_FAILED', label=_('WhatsApp Subscribed Failed'))
    WHATSAPP_UNSUBSCRIBED_FAILED = ChoiceItem(value='WHATSAPP_UNSUBSCRIBED_FAILED',
                                              label=_('WhatsApp Unsubscribed Failed'))
    WHATSAPP_CHATBOT_SUBSCRIBED = ChoiceItem(value='WHATSAPP_CHATBOT_SUBSCRIBED',
                                             label=_("WhatsApp chatbot subscribed"))
    WHATSAPP_CHATBOT_UNSUBSCRIBED = ChoiceItem(value='WHATSAPP_CHATBOT_UNSUBSCRIBED',
                                               label=_("WhatsApp chatbot Unsubscribed"))
    WHATSAPP_CHATBOT_SUBSCRIBED_FAILED = ChoiceItem(value='WHATSAPP_CHATBOT_SUBSCRIBED_FAILED',
                                                    label=_('WhatsApp chatbot Subscribed Failed'))
    WHATSAPP_CHATBOT_UNSUBSCRIBED_FAILED = ChoiceItem(value='WHATSAPP_CHATBOT_UNSUBSCRIBED_FAILED',
                                                      label=_('WhatsApp chatbot Unsubscribed Failed'))
