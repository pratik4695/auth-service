from django.conf import settings
from .smsproviders import *


class Communication:
    def send_sms(sms_to, message, priority, provider=None):
        if not provider:
            provider = settings.DEFAULT_SMS_PROVIDER

        provider = Communication._get_provider(provider)
        sms_from = None
        provider.send_message(
            sms_from=sms_from, 
            sms_to=sms_to,
            message=message,
            priority=priority
        )

    def _get_provider(provider):
        try:
            provider = eval(provider)
        except:
            provider = None

        return provider
