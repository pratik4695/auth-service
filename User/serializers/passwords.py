from rest_framework.serializers import ModelSerializer

from authentication.models.passwords import PasswordResetToken
from authentication.models.user import AttendanceJWTToken


class PasswordResetTokenSerializer(ModelSerializer):
    """
    Created By: Pratik Gupta
    Created On: 02/06/2021
    """

    class Meta:
        model = PasswordResetToken
        fields = ('user', 'hash_code', 'expires')
