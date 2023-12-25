from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import CustomUser
from django.utils.translation import gettext_lazy as _


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email',  'first_name', 'last_name')


class UserRegisSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'confirm_password', 'first_name', 'last_name')
        extra_kwargs = {
            'username': {'write_only': True},
            'email': {'write_only': True},
            'password': {'write_only': True},
            'first_name': {'required': False,'write_only': True},
            'last_name': {'required': False,'write_only': True},
        }

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            # Validate the password using Django's password validation.
            validate_password(password, self.instance)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        username_validator = CustomUsernameValidator(min_length=3)
        username = data.get('username')

        try:
            username_validator(username)
        except ValidationError as e:
            raise serializers.ValidationError({'username': str(e)})

        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data.get('email', ''),
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CustomUsernameValidator(UnicodeUsernameValidator):
    def __init__(self, min_length=3, *args, **kwargs):
        self.min_length = min_length
        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        if len(value) < self.min_length:
            raise ValidationError(
                _("Username must be at least %(min_length)d characters long."),
                code='username_too_short',
                params={'min_length': self.min_length},
            )
        if not value.isalnum():
            raise ValidationError(
                _("Username must contain only letters and numbers."),
                code='username_invalid_characters',
            )


