from core.grpc_exceptions import ValidationError


def validate_password(password):
    password_len = len(password)
    if not password_len in range(8, 21):
        raise ValidationError("Length of password should be between 8 to 20 characters")
