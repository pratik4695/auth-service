from django.db import models
from model_utils.models import TimeStampedModel

from User.constants import UserHistoryActions


class UserHistory(TimeStampedModel):
    user = models.ForeignKey('User.User', related_name='history_set', on_delete=models.CASCADE)
    action = models.CharField(max_length=65, choices=UserHistoryActions.choices,
                              validators=[UserHistoryActions.validator])
    pre_value = models.CharField(max_length=255, null=True, blank=True)
    post_value = models.CharField(max_length=255, null=True, blank=True)
    modified_by = models.ForeignKey('User.User', null=True, on_delete=models.SET_NULL)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.action
