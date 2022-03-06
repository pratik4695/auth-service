from celery.utils.log import get_task_logger
from django.conf import settings

from config.worker import app
from core.tasks import EmailTaskMeta

logger = get_task_logger(__name__)


class PasswordResetEmailNotificationToUser(EmailTaskMeta):
    notification_name = 'password_reset_email'
    template = 'reset_pwd_email_template.html'

    def __init__(self, user, password_reset_token):
        super().__init__()
        self.user = user
        self.hash_code = password_reset_token.get("hash_code")
        self.expires = password_reset_token.get("expires")
        self.logger = logger

    def get_subject(self):
        subject = 'Reset your password'
        return subject

    def get_reset_link(self):
        url = '{}/password/reset?user_type={}&hash_code={}&expires={}'.format(
            settings.PAYROLL_WEBSITE_URL, self.user.user_type, self.hash_code, self.expires)
        print("This is the url == {}".format(url))
        return url

    def get_recipient(self):
        return {
            'email': self.user.email
        }

    def handlebars(self):
        return {
            "first_name": self.user.first_name,
            # "last_name": self.user.last_name,
            "login_link": self.get_reset_link()
        }

    @app.task
    def send_user_reset_password_email(self):
        logger.info('Sending reset email to {}'.format(self.user.email))
        self.send_notification()
