from collections import namedtuple

import requests
from celery import Celery
from django.conf import settings
from django.core.files.storage import default_storage
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule
from requests import RequestException


def get_absolute_url(relative_file_path):
    if relative_file_path is None and relative_file_path == '':
        return ""
    path = relative_file_path.strip() if relative_file_path else relative_file_path
    if not path or path.startswith('http'):
        return path
    if hasattr(default_storage, "bucket_name") and default_storage.bucket_name:
        return default_storage.url(name=path)
    else:
        return settings.SITE_ADDRESS + "/media/" + path


def named_tuple_fetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


class RecognizeUserAPI:
    def __init__(self, email: str = None):

        if email is None:
            raise ValueError("email cannot be null")

        self._email = email

    def get_user_details(self) -> dict:
        url = "{}/api/v4/recognize_user/".format(settings.ROOT_API_URL)
        # url = 'http://127.0.0.1:8000/api/v4/recognize_user/'

        res = requests.get(url, headers={"x-aj-platform": "1"},
                           params={'username': self._email, 'check_cross_platform': 'true'})

        if res.status_code != 200:
            raise RequestException("Failed to get Recognize User API response, status: {} received response: {}".format(
                res.status_code, res.content))

        return res.json()


class GetUserDetailsAPI:
    def __init__(self, id: str = None):

        if id is None:
            raise ValueError("id cannot be null")

        self._id = id

    def get_user_details(self) -> dict:
        url = "{0}/api/v4/user/{1}".format(settings.ROOT_API_URL, self._id)

        res = requests.get(url, headers={"x-aj-platform": "1",
                                         "Authorization": "Bearer " + settings.RECRUIT_API_ADMIN_TOKEN})

        if res.status_code != 200:
            raise RequestException("Failed to get Recognize User API response, status: {} received response: {}".format(
                res.status_code, res.content))

        return res.json()


class CreatePeriodicTask:
    task_countdown = 1
    celery_queue = settings.CELERY_TASK_DEFAULT_QUEUE
    logger = None

    def __init__(self):
        self.name = self.get_task_name()
        self.task = self.get_task()

    def get_task(self):
        raise NotImplementedError("Override the \'set_task\' method.")

    def get_task_name(self):
        raise NotImplementedError("Override the \'set_task_name\' method.")

    def create_by_schedule(self, interval: int, interval_unit: IntervalSchedule.PERIOD_CHOICES) -> PeriodicTask:
        schedule, _ = IntervalSchedule.objects.get_or_create(every=interval, period=interval_unit)
        periodic_task = PeriodicTask.objects.get_or_create(interval=schedule, task=self.task, name=self.name)

        return periodic_task

    def create_by_cron(self, min=None, hour=None, week_day=None, month_day=None, year_month=None) -> PeriodicTask:
        minute = '*' if min is None else str(min)
        hour = '*' if hour is None else str(hour)
        day_of_week = '*' if week_day is None else str(week_day)
        day_of_month = '*' if month_day is None else str(month_day)
        month_of_year = '*' if year_month is None else str(year_month)

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year
        )

        periodic_task, _ = PeriodicTask.objects.get_or_create(crontab=schedule, task=self.task, name=self.name)

        return periodic_task

    def _get_task_functions(self):
        method_names = self.__dir__()
        functions = []
        for method_name in method_names:
            method = getattr(self, method_name)
            if hasattr(method, "app") and isinstance(getattr(method, 'app'), Celery):
                functions.append(method)
        if len(functions) != 1:
            self.logger.error(
                "******Only one shared task should be declared in a task Currently there is/are {}*******".
                    format(len(functions)))
            return None
        return functions[0]

    def __call__(self):
        task_function = self._get_task_functions()
        if task_function is None:
            return
        task_function.apply_async((self,), countdown=self.task_countdown, queue=self.celery_queue, )
