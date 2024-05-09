import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Create a superuser'

    def handle(self, *args, **options):
        User = get_user_model()
        superuser = User.objects.create(
            username=os.getenv('SUPERUSER_NAME'),
            is_superuser=True,
            is_staff=True,
            is_active=True
        )

        superuser.set_password(os.getenv('SUPERUSER_PASSWORD'))
        superuser.save()
