"""Write-side business logic for the accounts bounded context."""
from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(data: dict) -> User:
    password = data.pop("password", None)
    return User.objects.create_user(password=password, **data)


def update_user(instance: User, data: dict) -> User:
    password = data.pop("password", None)
    for attr, value in data.items():
        setattr(instance, attr, value)
    instance.save()
    if password is not None:
        instance.set_password(password)
        instance.save(update_fields=["password"])
    return instance
