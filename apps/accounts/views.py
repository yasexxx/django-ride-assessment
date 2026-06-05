"""ViewSets for the accounts bounded context."""
from django.contrib.auth import get_user_model

from apps.accounts.serializers import UserSerializer
from apps.common.viewsets import AdminModelViewSet

User = get_user_model()


class UserViewSet(AdminModelViewSet):
    queryset = User.objects.all().order_by("id_user")
    serializer_class = UserSerializer
