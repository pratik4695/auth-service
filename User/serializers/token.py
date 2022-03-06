from rest_framework.serializers import ModelSerializer

from User.models import UserJWTToken


class UserJWTTokenSerializer(ModelSerializer):
    """
    """

    class Meta:
        model = UserJWTToken
        fields = ('user', 'access_token', 'refresh_token', 'expires')
