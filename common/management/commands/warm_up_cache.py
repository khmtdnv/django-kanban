from django.core.cache import cache
from django.core.management.base import BaseCommand

from apps.accounts.models import User
from common.utils import get_projects_list_cache_key, get_user_projects_list


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            cache_key = get_projects_list_cache_key(user.id)  # type: ignore
            data = get_user_projects_list(user)
            cache.set(cache_key, data, timeout=60)
            self.stdout.write(
                f" - Кэш прогрет для {user.phone_number} (Key: {cache_key})"
            )
        self.stdout.write("all good")
