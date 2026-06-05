"""Serializers for the accounts (User) bounded context."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

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
        # Bypasses super().create() deliberately: user creation must route
        # through the manager to hash the password.
        password = validated_data.pop("password", None)
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance: User, validated_data: dict) -> User:
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password is not None:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user
