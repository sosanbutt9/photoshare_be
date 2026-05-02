from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class RegistrationError(Exception):
    def __init__(self, message, code="registration_error"):
        self.message = message
        self.code = code
        super().__init__(message)


@transaction.atomic
def register_consumer(
    *,
    email: str,
    username: str,
    password: str,
    full_name: str = "",
    role: str | None = None,
) -> User:
    email_norm = User.objects.normalize_email(email)
    if User.objects.filter(email__iexact=email_norm).exists():
        raise RegistrationError("An account with this email already exists.", code="email_taken")
    if User.objects.filter(username__iexact=username).exists():
        raise RegistrationError("This username is already taken.", code="username_taken")
    resolved_role = role or User.Role.CONSUMER
    if resolved_role not in (User.Role.CONSUMER, User.Role.CREATOR):
        raise RegistrationError("Invalid role for self-registration.", code="invalid_role")
    user = User.objects.create_user(
        email=email_norm,
        username=username,
        password=password,
        full_name=full_name or "",
        role=resolved_role,
    )
    return user
