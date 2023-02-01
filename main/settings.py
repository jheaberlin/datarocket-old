import os
import environ
import mimetypes
from pathlib import Path
from django.conf import settings

mimetypes.add_type("text/css", ".css", True)

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = env("DEBUG")

SECRET_KEY = env("SECRET_KEY")

CSRF_TRUSTED_ORIGINS = env.list("CRSF_TRUSTED_ORIGINS")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "huey.contrib.djhuey",
    "rest_framework",
    "storages",
    "datarocket",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "main.urls"

AUTH_USER_MODEL = "datarocket.customUser"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "main.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

HUEY = {
    "huey_class": "huey.RedisHuey",
    "name": settings.DATABASES["default"]["NAME"],
    "results": True,
    "store_none": True,
    "immediate": False,
    "utc": True,
    "blocking": True,
    "connection": {
        "host": env("REDIS_HOST"),
        "port": env("REDIS_PORT"),
        "db": env("REDIS_DB"),
        "password": env("REDIS_PASSWORD"),
        "connection_pool": None,
        "read_timeout": 1,
        "url": None,
    },
    "consumer": {
        "workers": 20,
        "worker_type": "thread",
        "initial_delay": 0.1,
        "backoff": 1.15,
        "max_delay": 10.0,
        "scheduler_interval": 1,
        "periodic": True,
        "check_worker_health": True,
        "health_check_interval": 1,
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = os.path.join(BASE_DIR, "temp/")
MEDIA_ROOT = os.path.join(BASE_DIR, "temp/")
