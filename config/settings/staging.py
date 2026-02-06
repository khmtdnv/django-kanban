import os
from datetime import timedelta

from decouple import Config, Csv, RepositoryEnv

from .base import *

env_path = os.path.join(
    BASE_DIR,
    ".env.staging",
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
    default="localhost,127.0.0.1",
)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=Csv(),
    default="http://localhost:8000,http://127.0.0.1:8000",
)

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT"),
    }
}

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
        "drf_yasg",
    ]
    # MIDDLEWARE += [
    #     "debug_toolbar.middleware.DebugToolbarMiddleware",
    # ]
    INTERNAL_IPS = [
        "127.0.0.1",
        "::1",
    ]


SIMPLE_JWT.update(
    {
        "SIGNING_KEY": SECRET_KEY,
        "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    }
)


CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")


def show_toolbar(request):
    return True


# DEBUG_TOOLBAR_CONFIG = {
#     "SHOW_TOOLBAR_CALLBACK": show_toolbar,
# }
SWAGGER_USE_COMPAT_RENDERERS = False
