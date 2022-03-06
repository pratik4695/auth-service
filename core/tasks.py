import requests
from celery import Celery
from django.conf import settings
from notificationhub_sdk import Push, Task, EmailRecipient, EmailAttachment, Email
from notificationhub_sdk.common import MessageType, ClientPlatform

from config.settings import app_settings
from core.constants import PlatformType, PlatformBucket, MobilePushClient
from core.helpers import RecognizeUserAPI


class PushTaskMeta:
    AUTH_TOKEN = settings.RECRUIT_API_ADMIN_TOKEN
    notification_name = ""
    template = ""
    extra_payload = None
    sent_by_id = None
    task_countdown = 1
    celery_queue = settings.CELERY_PUSH_TASK_QUEUE
    message_type = MessageType.TRANSACTIONAL  # default is TRANSACTIONAL
    logger = None

    def __init__(self):
        self.sent_by_id = None
        self.user_id = None
        self.handlebar_dict = {}
        self.arn_endpoints = None

    def get_arn_endpoints(self):
        url = "{}/api/v1/push_manager/".format(settings.ROOT_API_URL, self.user_id)
        res = requests.get(url=url, params={"user_id": self.user_id},
                           headers={"Authorization": "Bearer {}".format(self.AUTH_TOKEN)})
        if res.status_code != 200:
            print("Failed to fetch the token, received response: {}".format(res.content))
        else:
            client_map = {
                MobilePushClient.CANDIDATE_ANDROID_MOBILE: ClientPlatform.ANDROID,
                MobilePushClient.CANDIDATE_MOBILE_WEB: ClientPlatform.WEB,
                MobilePushClient.STAFFING_ANDROID_MY_HR_APP: ClientPlatform.ANDROID,
                MobilePushClient.STAFFING_IOS_MY_HR_APP: ClientPlatform.IOS
            }
            # print(res.json())
            result_obj = res.json()  # dict obj
            for value in result_obj['objects']:
                value['client'] = client_map[value['client']]
            obj_list = result_obj['objects']  # list of dict for each record
            return obj_list
        return None

    def _validate(self):
        if not self.arn_endpoints:
            self.logger.error("\'arn_endpoints\' cannot be empty.")
            return False
        # Notification Name Sanity Check
        elif self.notification_name is None or self.notification_name == "":
            self.logger.error("\'notification_name\' cannot be empty/null.")
            return False
        # Template Sanity Check
        if self.template is None or self.template == "":
            self.logger.error("\'template\' cannot be empty/null.")
            return False
        if not self.validate():
            return False
        return True

    def validate(self):
        """
        Override this if extra validation needs to be done.
        :return:
        """
        return True

    def handlebars(self):
        """
        Override this
        :return:
        """
        raise NotImplementedError("Override the \'handlebars\' method.")

    def set_extra_payload(self):
        """
        Override this if extra payloads needed .
        :return:
        """
        return self.extra_payload

    def get_template(self):
        """
        Override this, if wanna apply some logic on template url retrieval
        :return:
        """
        return self.template

    def set_template_url(self):
        return "%s%s/attendance/push/%s" % (
            settings.NOTIFICATION_TEMPLATE_BASE_URL, PlatformBucket.OLX_PEOPLE, self.template)

    def get_notification_name(self):
        """
        Override this, if wanna apply some logic on notification_name retrieval
        :return:
        """
        return self.notification_name

    def send_notification(self):
        self.notification_name = self.get_notification_name()
        self.arn_endpoints = self.get_arn_endpoints()
        self.template = self.get_template()
        template_url = self.set_template_url()
        self.handlebar_dict = self.handlebars()
        self.extra_payload = self.set_extra_payload()
        self.logger.info(
            "Attempting to send Push notification \'{0}\' to user {1}".format(self.notification_name, self.user_id))
        if not self._validate():
            self.logger.error(
                "can't send the Push notification \'{0}\' to user {1} because initial validation failed".format(
                    self.notification_name, self.user_id))
            return
        if self.arn_endpoints and self.handlebar_dict and template_url and self.user_id:
            for token_obj in self.arn_endpoints:
                token_value = token_obj['token']
                client_value = token_obj['client']
                push = Push(token=token_value, template=template_url, context=self.handlebar_dict,
                            extra_payload=self.extra_payload, user_id=self.user_id, client_platform=client_value)
                task = Task(name=self.notification_name, sent_by_id="test", client='staffing-attendance-api',
                            platform=PlatformType.OLX_PEOPLE, message_type=self.message_type, push=push)
                try:
                    task_id, msg_id = task.send()
                    self.logger.info("Successfully sent task {} to SQS with messageId {}".format(task_id, msg_id))
                except Exception as ex:
                    self.logger.error("Failed to send task to SQS, reason: {}".format(ex))
        else:
            self.logger.error("can't send the Push notification \'{0}\' to user {1} as required data to create push is "
                              "not available".format(self.notification_name, self.user_id))
            return

    def _get_task_functions(self):
        method_names = self.__dir__()
        functions = []
        for method_name in method_names:
            method = getattr(self, method_name)
            if hasattr(method, "app") and isinstance(getattr(method, 'app'), Celery):
                functions.append(method)
        if len(functions) != 1:
            self.logger.error(
                "Only one shared task should be declared in a task Currently there is/are {}".format(len(functions)))
            return None
        return functions[0]

    def __call__(self):
        task_function = self._get_task_functions()
        if task_function is None:
            return
        task_function.apply_async((self,), countdown=self.task_countdown, queue=self.celery_queue, )


class EmailTaskMeta:
    notification_name = ""
    template = ""
    skip_email_verification = False
    skip_subscription = False
    message_type = MessageType.TRANSACTIONAL  # Default is transactional message
    _default_send_from = "noreply@olxpeople.com"
    _default_from_name = "Olx People"
    _default_reply_to = "noreply@olxpeople.com"
    _default_signature = "Team OLX People"
    _default_cc = []
    _default_attachments = []
    skip_email_on_null_data = False
    # Task countdown
    task_countdown = 1
    celery_queue = settings.CELERY_EMAIL_TASK_QUEUE
    logger = None

    def __init__(self):
        self.recipient = None
        self.reply_to = None
        self.handlebar_dict = {}

    def get_recipient(self):
        """
        Override this and return a user dict as per user.proto file
        User {
          string id = 1;
          string first_name = 2;
          string last_name = 3;
          UserType user_type = 4;
          string email = 5;
          string mobile = 6;
          int64 created = 16;
          bool email_verified = 7;
          bool mobile_verified = 8;
          bool email_subscribed = 17;
          bool sms_subscribed = 18;
          Gender gender = 19;
          string password = 9;
          UserEntity entity = 10;
          bool password_exists = 20;
        }
        :return:
        """
        raise NotImplementedError("Override the \'get_recipient\' method.")

    def get_notification_name(self):
        """
        Override this, if wanna apply some logic on notification_name retrieval
        :return:
        """
        return self.notification_name

    def get_template(self):
        """
        Override this, if wanna apply some logic on template url retrieval
        :return:
        """
        return self.template

    def set_template_url(self):
        self.template = "%s%s/attendance/email/%s" % (
            settings.NOTIFICATION_TEMPLATE_BASE_URL, PlatformBucket.OLX_PEOPLE, self.template)
        return self.template

    def get_send_from(self):
        return self._default_send_from

    def get_from_name(self):
        return self._default_from_name

    def get_reply_to(self):
        return {
            'email': self._default_reply_to
        }

    def get_cc(self):
        return self._default_cc

    def get_subject(self):
        raise NotImplementedError("Override the \'get_subject\' method.")

    def extra_handling(self, **kwargs):
        """
        Override this if you wanna do something peculiar
        :return:
        """
        pass

    def get_attachments(self):
        return self._default_attachments

    def handlebars(self):
        """
        Override this
        :return:
        """
        raise NotImplementedError("Override the \'handlebars\' method.")

    def get_signature(self):
        """
        Override this in your email task if you need signature something else then the default values
        :return: Returns the text for signature
        """
        return self._default_signature

    def _add_default_handlebars(self):
        facebook_link = "https://www.facebook.com/OlxPeople-627201761121386"
        linkedin_link = "https://www.linkedin.com/company/14702596"
        youtube_link = "https://www.youtube.com/channel/UCkjEYqhAdy5ew8xTZlYQkBg?reload=9"
        twitter_link = "https://twitter.com/olxpeople"
        website = settings.RECRUIT_WEBSITE_URL
        self.handlebar_dict.update({
            "fb_link": facebook_link,
            "li_link": linkedin_link,
            "yt_link": youtube_link,
            "tw_link": twitter_link,
            "website": website,
            "signature": self.get_signature()
        })

    def _append_utm_parameters(self, url):
        utm_source = "olxPeople"
        utm_medium = "email"
        utm_campaign = self.notification_name
        connector = '&' if '?' in url else '?'
        url = "{0}{1}utm_source={2}&utm_medium={3}&utm-campaign={4}". \
            format(url, connector, utm_source, utm_medium, utm_campaign)
        return url

    def _validate(self):
        # Recipient Sanity Check
        assert isinstance(self.recipient, dict), "recipient should be a dict"

        # Notification Name Sanity Check
        if self.notification_name is None or self.notification_name == "":
            self.logger.error("\'notification_name\' cannot be empty/null.")
            return False
        # Template Sanity Check
        if self.template is None or self.template == "":
            self.logger.error("\'template\' cannot be empty/null.")
            return False
        if not self.sanitize_email():
            return False
        # Custom Validation Checks
        if not self.validate():
            return False
        return True

    def validate(self):
        """
        Override this if extra validation needs to be done.
        :return:
        """
        return True

    def sanitize_email(self):
        user = self.recipient
        user_id = user.get("id")
        email = user.get("email")
        email_verified = user.get("email_verified", False)
        email_subscribed = user.get("email_subscribed", False)

        if email is None:
            self.logger.warning("User (ID:{0}) has no email configured.".format(user_id))
            return False
        if not self.skip_email_verification and not email_verified:
            self.logger.warning("User's (ID:{0}) email \'{1}\' is not verified.".format(user_id, email))
            return False
        if not self.skip_subscription and not email_subscribed:
            self.logger.warning("User (ID:{0}) has not subscribed for Email notifications.".format(user_id))
            return False
        return True

    def get_sent_by(self):
        try:
            user = RecognizeUserAPI(email=settings.SYSTEM_ADMIN_USER_EMAIL).get_user_details()
            return user['id']
        except Exception as ex:
            self.logger.error(ex)
            return 'test'

    def get_cc_list(self):
        final_cc_list = []
        cc_list = self.get_cc()
        for email in cc_list:
            if email is not None:
                final_cc_list.append(EmailRecipient(email=email))
        return final_cc_list

    def get_attachments_list(self):
        final_attachments = []
        attachments = self.get_attachments()
        for attachment in attachments:
            final_attachments.append(EmailAttachment(file_name=attachment.data.get('filename'),
                                                     url=attachment.data.get('fileUrl')))
        return final_attachments

    def send_notification(self):
        self.recipient = self.get_recipient()
        self.reply_to = self.get_reply_to()
        self.notification_name = self.get_notification_name()
        self.template = self.get_template()
        template_url = self.set_template_url()
        self.logger.info("Attempting to Email \'{0}\' to {1}".format(self.notification_name, self.recipient["email"]))
        if not self._validate():
            return
        self.handlebar_dict = self.handlebars()
        if self.skip_email_on_null_data and not self.handlebar_dict:
            self.logger.error("Not sending email as handlebars() returned null.")
            return
        self.extra_handling()
        self._add_default_handlebars()

        send_to = EmailRecipient(email=self.recipient["email"], name=self.recipient.get("name", ''),
                                 user_id=self.recipient.get("id", ''))
        reply_to = EmailRecipient(email=self.reply_to["email"], name=self.reply_to.get("name", ''),
                                  user_id=self.reply_to.get("id", ''))

        email = Email(send_to=[send_to], subject=self.get_subject(),
                      template=template_url, attachments=self.get_attachments_list(),
                      context=self.handlebar_dict, sender=EmailRecipient(name=self.get_from_name(),
                                                                         email=self.get_send_from()),
                      cc=self.get_cc_list(), reply_to=reply_to)
        task = Task(name=self.notification_name, sent_by_id=self.get_sent_by(), client='staffing-attendance-api',
                    platform=PlatformType.OLX_PEOPLE, email=email, message_type=self.message_type)
        try:
            task_id, msg_id = task.send()
            self.logger.info("Successfully sent task {} to SQS with messageId {}".format(task_id, msg_id))
        except Exception as ex:
            self.logger.error("Failed to send task to SQS, reason: {}".format(ex))

    def _get_olx_people_default_handlebars(self):
        facebook_link = "https://www.facebook.com/OlxPeople-627201761121386"
        linkedin_link = "https://www.linkedin.com/company/14702596"
        youtube_link = "https://www.youtube.com/channel/UCkjEYqhAdy5ew8xTZlYQkBg?reload=9"
        twitter_link = "https://twitter.com/olxpeople"
        website = 'www.olxpeople.com'
        return {
            "fb_link": facebook_link,
            "li_link": linkedin_link,
            "yt_link": youtube_link,
            "tw_link": twitter_link,
            "website": website,
            "signature": self.get_signature()
        }

    def _get_task_functions(self):
        method_names = self.__dir__()
        functions = []
        for method_name in method_names:
            method = getattr(self, method_name)
            if hasattr(method, "app") and isinstance(getattr(method, 'app'), Celery):
                functions.append(method)
        if len(functions) != 1:
            self.logger.error(
                "Only one shared task should be declared in a task Currently there is/are {}".format(len(functions)))
            return None
        return functions[0]

    def __call__(self):
        task_function = self._get_task_functions()
        if task_function is None:
            return
        task_function.apply_async((self,), countdown=self.task_countdown, queue=self.celery_queue)
