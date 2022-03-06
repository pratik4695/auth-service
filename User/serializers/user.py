from rest_framework.fields import (CharField, EmailField, UUIDField, IntegerField)
from rest_framework.serializers import ModelSerializer, ValidationError

from User.models import User
from User.services.helper import contains_profane
from User.services.validators import mobile_validator_with_specific_error


class UserSerializer(ModelSerializer):
    """
    """
    id = UUIDField(format='hex_verbose', required=False)
    # created_by = UserShortSerializer(allow_null=True, required=False)
    # created_by_id = PrimaryKeyRelatedField(queryset=User.objects, write_only=True, required=False)
    email = EmailField(required=False, write_only=True)
    mobile = CharField(required=False, write_only=True, max_length=10,
                       validators=[mobile_validator_with_specific_error])
    password = CharField(max_length=255, required=False, write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'mobile', 'is_active', 'user_type', 'created', 'modified', 'first_name',
            'last_name', 'password', 'mobile_encrypted', 'email_encrypted', 'date_of_birth', 'gender', 'is_active',
            'is_admin'
        )
        read_only_fields = ("email_encrypted", "mobile_encrypted", 'created', 'modified')

    @staticmethod
    def check_for_profanity(attrs):
        if attrs.get("first_name") and contains_profane(word=attrs.get("first_name")):
            raise ValidationError("First name contains unaccepted words/phrases.")
        if attrs.get("last_name") and contains_profane(word=attrs.get("last_name")):
            raise ValidationError("Last name contains unaccepted words/phrases.")
        if attrs.get("email") and contains_profane(word=attrs.get("email"), is_email=True):
            raise ValidationError("Email address contains unaccepted words/phrases.")

    @staticmethod
    def strip(data):
        if not data:
            return data
        return data.strip()

    def clean_data(self, validated_data):
        if validated_data.get("first_name"):
            validated_data['first_name'] = self.strip(validated_data.get("first_name"))
        if validated_data.get("last_name"):
            validated_data['last_name'] = self.strip(validated_data.get("last_name"))
        if validated_data.get("email"):
            validated_data["email"] = self.strip(validated_data["email"])
        if validated_data.get("mobile"):
            validated_data["mobile"] = self.strip(validated_data["mobile"])
        return validated_data

    def __update_mobile(self, user, mobile):
        if not mobile:
            return

        user._set_mobile(
            mobile=mobile,
            auto_save=False,
        )

    def __update_email(self, user, email):
        if not email:
            return

        user._set_email(
            email=email,
            auto_save=False,
        )

    def __add_password(self, user, new_password):
        if not new_password:
            return

        if user.password_exists:
            raise ValidationError({"password": ["Value already exists for user."]})

        user._set_password(new_password)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        validated_data = self.clean_data(validated_data)
        self.check_for_profanity(validated_data)
        self.__update_mobile(instance, validated_data.get("mobile"))
        self.__update_email(instance, validated_data.get("email"))
        # # Set the password
        # self.__add_password(instance, password)

        for field, val in validated_data.items():
            setattr(instance, field, val)
        instance.save()

        return instance

    def create(self, validated_data):
        """
        :param validated_data:
        :return:
        """
        email = validated_data.get("email")
        mobile = validated_data.get("mobile")

        # Create User Instance
        validated_data = self.clean_data(validated_data)
        self.check_for_profanity(validated_data)

        user = User.objects.create(**validated_data)
        #
        # user._set_password()
        # user.save()

        return user


class UserShortSerializer(ModelSerializer):
    """
    Created By: Pratik Gupta
    Created On: 03/12/2020
    """

    # email = serializers.SerializerMethodField()
    # mobile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'user_type', 'first_name', 'last_name'
        )


class UserListShortSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'user_type', 'first_name', 'last_name'
        )
