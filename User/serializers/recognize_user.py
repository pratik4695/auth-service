from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from User.models import User


class RecognizeUserSerializer(ModelSerializer):
    """
    with provided username, recognize the user, whether he is exist or not
    Created by Pratik Gupta
    on 29/05/2021
    """
    email = SerializerMethodField()
    mobile = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'user_type', 'email', 'mobile'
        )

    @staticmethod
    def get_email(user: User):
        user.decrypt_email()
        email = user.email
        if email:
            email_arr = email.split('@')
            start_email = "".join('*' if email_char_index % 3 else email_arr[0][email_char_index] for email_char_index
                                  in range(len(email_arr[0])))
            email = "{0}@{1}".format(start_email, email_arr[1])
        return email

    @staticmethod
    def get_mobile(user: User):
        user.decrypt_mobile()
        mobile = user.mobile
        if mobile:
            mobile = mobile.replace(mobile[1:-3], '*' * 6)
        return mobile
