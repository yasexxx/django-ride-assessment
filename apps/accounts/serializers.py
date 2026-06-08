"""Serializers for the accounts (User) bounded context."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.services import create_user, update_user

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Read/write serializer for User.

    ``password`` is write-only; creation is delegated to the ``create_user``
    manager so hashing happens in exactly one place.
    """
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "id_user",
            "role",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
        ]
        read_only_fields = ["id_user"]

    def create(self, validated_data: dict) -> User:
        return create_user(validated_data)

    def update(self, instance: User, validated_data: dict) -> User:
        return update_user(instance, validated_data)
