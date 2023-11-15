import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(verbose=True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'RENDER' not in os.environ
if os.environ.get("DEBUG", "False") == "True":
    DEBUG = True

X_FRAME_OPTIONS = 'ALLOWALL'

XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']

ALLOWED_HOSTS = ['*']

CORS_ALLOW_HEADERS = "*"
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "compressor",
    "corsheaders",
    "django_countries",
    "djmoney",
    "phonenumber_field",
    "rest_framework",
    "storages",
    "tailwind",
    "tailwind_theme",
    "pommento.auth",
    "pommento.billing",
    "pommento.utils",
    "pommento.core"
]

if DEBUG is True:
    INSTALLED_APPS.append("django_browser_reload")
    INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG is True:
    MIDDLEWARE.insert(0, "django_browser_reload.middleware.BrowserReloadMiddleware")
    MIDDLEWARE.insert(0, "pyinstrument.middleware.ProfilerMiddleware")

ROOT_URLCONF = "pommento.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "pommento.context_processors.google_oauth_client_id",
                "pommento.context_processors.stripe_publishable_key",
            ],
        },
    },
]

WSGI_APPLICATION = "pommento.wsgi.application"


CORS_ORIGIN_ALLOW_ALL = True


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {    
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase', 
    }}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "pommento_auth.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "/login/"
LOGOUT = ""

# Caches
# https://docs.djangoproject.com/en/4.1/ref/settings/#caches

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-US"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
if DEBUG is True:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_HOST = os.environ.get("STATIC_HOST")
STATICFILES_DIRS = [
    STATIC_DIR,
]
STATIC_URL = "/static/"


COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"
COMPRESS_ROOT = os.path.join(BASE_DIR, "staticfiles")
if DEBUG is True:
    COMPRESS_ROOT = os.path.join(BASE_DIR, "static")
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = True

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]


# Django Tailwind

TAILWIND_APP_NAME = "tailwind_theme"


# Email configurations
# https://docs.djangoproject.com/en/4.1/topics/email/

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
if os.environ.get("EMAIL_USE_TLS", "True") == "False":
    EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")


# Google

GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", None)
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", None)


# Stripe

STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", None)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", None)
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", None)
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", None)


# pommento config

SUBSCRIPTION_TRIAL_PERIOD_DAYS = 14

AUTH_USER_NAME_MAX_LENGTH = int(os.environ.get("AUTH_USER_NAME_MAX_LENGTH", "150"))

# Pangea
PANGEA_DOMAIN = os.environ.get('PANGEA_DOMAIN')
PANGEA_TOKEN = os.environ.get('PANGEA_TOKEN')