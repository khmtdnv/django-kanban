import os
from datetime import timedelta

from decouple import Config, Csv, RepositoryEnv

from .base import *

env_path = os.path.join(
    BASE_DIR,
    ".env",
)
config = Config(RepositoryEnv(env_path))

SECRET_KEY = config("SECRET_KEY")
DEBUG = config(
    "DEBUG",
    cast=bool,
    default=True,
)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=Csv(),
)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=Csv(),
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT"),
    }
}

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INTERNAL_IPS = [
        "127.0.0.1",
        "::1",
    ]


SIMPLE_JWT.update(
    {
        "SIGNING_KEY": SECRET_KEY,
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    }
)


CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")
