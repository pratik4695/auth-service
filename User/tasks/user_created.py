from celery.utils.log import get_task_logger
from django.conf import settings

from authentication.models import User
from config.worker import app
from core.tasks import EmailTaskMeta

logger = get_task_logger(__name__)


class UserCreatedEmailNotification(EmailTaskMeta):
    notification_name = 'reporting_manager_created_email'
    template = 'rm_login_credentials.html'
    task_countdown = 1 if settings.DEBUG else 43200
    use_attendance_template = True

    def __init__(self, password: str, user_id: str):
        super().__init__()
        self.password = password
        self.user = User.objects.get(id=user_id)
        self.logger = logger
        self.user.decrypt_data()

    def get_subject(self):
        subject = 'Login details for Payroll dashboard | Olx People'
        return subject

    def get_recipient(self):
        recipient = {
            'email': self.user.email,
            'email_verified': True,
            'email_subscribed': True
        }
        return recipient

    def handlebars(self):
        return {
            'first_name': self.user.name,
            'email': self.user.email,
            'password': self.password,
            'website_url': settings.PAYROLL_WEBSITE_URL,
            'login': settings.PAYROLL_WEBSITE_URL
        }

    @app.task
    def send_user_created_email(self):
        logger.info('Sending reporting manger credentials email to {}'.format(self.user.email))
        self.send_notification()
