from django.utils import timezone

from django.db import models
from model_utils.models import TimeStampedModel

from User.models import User


class PasswordResetToken(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hash_code = models.CharField(max_length=400)
    expires = models.DateTimeField()

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        if not self.expires:
            return True

        return timezone.now() >= self.expires
