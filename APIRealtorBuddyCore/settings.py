"""
Django settings for APIRealtorBuddyCore project.

Generated by 'django-admin startproject' using Django 3.2.23.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import ssl
from urllib.parse import urlparse
from pathlib import Path
from .config import (
    DATABASE_NAME,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
    CELERY_BROKER_URL_,
    CELERY_RESULT_BACKEND_,
    TWILIO_ACCOUNT_SID_,
    TWILIO_AUTH_TOKEN_,
    TWILIO_NUMBER_,
    G_CLIENT_ID,
    G_CLIENT_SECRET,
    DEBUG_,
    ALLOWED_HOSTS_,
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-&s5pkr1ftwa=td-ollnfus&86)av$+6tszmw6*p04-^v@)x+wi"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if DEBUG_ == "False" else True

ALLOWED_HOSTS = ALLOWED_HOSTS_.split(",")

# Celery Configuration
if urlparse(CELERY_BROKER_URL_).scheme == "rediss":
    CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE}
    CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL
CELERY_BROKER_URL = CELERY_BROKER_URL_
CELERY_RESULT_BACKEND = CELERY_RESULT_BACKEND_
BEAT_SCHEDULER = ("django_celery_beat.schedulers:DatabaseScheduler",)

# Twilio Configuration
TWILIO_ACCOUNT_SID = TWILIO_ACCOUNT_SID_
TWILIO_AUTH_TOKEN = TWILIO_AUTH_TOKEN_
TWILIO_NUMBER = TWILIO_NUMBER_


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_celery_beat",
    "corsheaders",
    "rest_framework",
    # "rest_framework_api_key",
    # "allauth",
    # "allauth.account",
    # "allauth.socialaccount",
    # "allauth.socialaccount.providers.google",
    "buildingService",
    "twilioService",
    "stripeService",
    "slackService",
    "loggingService",
    "clientOutreachService",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Moved up
    # "allauth.account.middleware.AccountMiddleware",
]

# REST_FRAMEWORK = {
#     "DEFAULT_PERMISSION_CLASSES": [
#         "rest_framework_api_key.permissions.HasAPIKey",
#     ]
# }

# SITE_ID = 1
# LOGIN_URL = "/accounts/login/"
# LOGIN_REDIRECT_URL = "/buildings"  # Adjust to your redirect URL

# AUTHENTICATION_BACKENDS = [
#     "django.contrib.auth.backends.ModelBackend",
#     "allauth.account.auth_backends.AuthenticationBackend",
# ]

# SOCIALACCOUNT_PROVIDERS = {
#     "google": {
#         "SCOPE": [
#             "profile",
#             "email",
#         ],
#         "AUTH_PARAMS": {
#             "access_type": "online",
#         },
#         "APP": {
#             "client_id": G_CLIENT_ID,
#             "secret": G_CLIENT_SECRET,
#         },
#         "EMAIL_AUTHENTICATION": True,
#     }
# }


CORS_ALLOW_ALL_ORIGINS = False  # Switch to False if specifying allowed origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://bumpy-moles-allow.loca.lt",
]

ROOT_URLCONF = "APIRealtorBuddyCore.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "APIRealtorBuddyCore/templates"),
        ],
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
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            os.path.join(BASE_DIR, "APIRealtorBuddyCore/templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "APIRealtorBuddyCore.jinja2.environment",
        },
    },
]

WSGI_APPLICATION = "APIRealtorBuddyCore.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # Consider setting to False to avoid disabling loggers
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "httpx": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "kombu": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "redis": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
