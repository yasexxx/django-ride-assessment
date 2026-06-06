from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with initial user data using 3 roles: admin, rider, and driver."

    DEFAULT_PASSWORD = "Test12345"

    def handle(self, *args, **options):
        USER_COUNTS = {
            User.Role.RIDER: 10,
            User.Role.DRIVER: 10,
        }

        for role, count in USER_COUNTS.items():
            for i in range(1, count + 1):
                email = f"{role}_{i}@email.com"

                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "first_name": f"{role.title()} {i}",
                        "role": role,
                    },
                )

                if created:
                    user.set_password(self.DEFAULT_PASSWORD)
                    user.save()

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Created {USER_COUNTS.get(User.Role.ADMIN, 0)} admin(s), "
                    f"{USER_COUNTS.get(User.Role.RIDER, 0)} rider(s), and "
                    f"{USER_COUNTS.get(User.Role.DRIVER, 0)} driver(s)."
                )
            )
        )