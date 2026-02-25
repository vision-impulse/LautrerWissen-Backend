# Copyright (c) 2025 Vision Impulse GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Authors: Benjamin Bischke

import os
import environ
from pathlib import Path
from ..settings_jazzmin import JAZZMIN_SETTINGS, JAZZMIN_UI_TWEAKS

def parse_admins(admins_env: str):
    admins = []
    for pair in admins_env.split(","):
        if ":" in pair:
            name, email = pair.split(":", 1)
            admins.append((name.strip(), email.strip()))
    return admins


def load_secrets(file_path):
    secrets = {}
    if not os.path.exists(file_path):
        return secrets

    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                secrets[key] = value
    return secrets

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# -----------------------------------------------------------------------------
#   Specific settings / configuration loaded via env vars and secrets
# -----------------------------------------------------------------------------
env = environ.Env()

# BB: inject env vars via docker compose, use local file only if started 
#  directly from cmd locally without docker.
env_file = BASE_DIR / ".env" 
if env_file.exists():
    env.read_env(env_file, overwrite=False)

# Security settings depending on the deployment and dev/prod environment
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost",])
CORS_ALLOWED_ORIGINS = env.list("DJANGO_CORS_ALLOWED_ORIGINS", default=[])
SESSION_COOKIE_DOMAIN = env("DJANGO_SESSION_COOKIE_DOMAIN", default=None)
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
CSRF_COOKIE_DOMAIN = env("DJANGO_CSRF_COOKIE_DOMAIN", default=None)

# App specific settings
FRONTEND_URL = env("DJANGO_FRONTEND_URL", default=None)
SCHEDULER_ENABLED = env.bool("DJANGO_SCHEDULER_ENABLED", default=False)

# DB settings
DB_PORT = env.int("DATABASE_PORT", default=5432)
DB_HOST = env("DATABASE_HOST", default="localhost")

# Email settings
EMAIL_ADMINS_TO = parse_admins(env("DJANGO_ADMINS_EMAILS_TO", default=""))
EMAIL_HOST = env('DJANGO_EMAIL_HOST') 
EMAIL_PORT = env.int("DJANGO_EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("DJANGO_EMAIL_USE_TLS", default=True)

# Redis settings
REDIS_HOST = env('REDIS_HOST', default="redis")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# Log settings
LOG_DIR = env("APP_LOG_DIR", default="/logs") # BB: For Docker,  use '.local' if django is started without docker
PRIVATE_MEDIA_ROOT = LOG_DIR 
os.makedirs(LOG_DIR, exist_ok=True)

# ---------------------------------------------------------------------------------
# SECURITY WARNING: Keep sensitive information used in production secret!
db_secrets = load_secrets("/run/secrets/db_secrets")
DB_PASSWORD = db_secrets.get("POSTGRES_PASSWORD") # SECURITY WARNING!
DB_USER = db_secrets.get("POSTGRES_USER") # SECURITY WARNING!
DB_NAME = db_secrets.get("POSTGRES_DB") # SECURITY WARNING!

django_secrets = load_secrets("/run/secrets/django_secrets")
EMAIL_HOST_USER = django_secrets.get("EMAIL_HOST_USER") # SECURITY WARNING!
EMAIL_HOST_PASSWORD = django_secrets.get("EMAIL_HOST_PASSWORD") # SECURITY WARNING!
SECRET_KEY = django_secrets.get("DJANGO_SECRET_KEY") # SECURITY WARNING!
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY not found in /run/secrets/django_secrets !")
# -----------------------------------------------------------------------------
#   DJANGO CORE SETTINGS
# -----------------------------------------------------------------------------
# See more info in https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Security settings!
CORS_ALLOW_ALL_ORIGINS = False
X_FRAME_OPTIONS = "DENY"

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'channels',
    'daphne',
    'webapp',
    'frontend_config',
    'pipeline_manager',
    'monitoring',
    'rest_framework',
    'django_filters',
    'corsheaders',
    "django_apscheduler",
    'lautrer_wissen.apps.LautrerWissenConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'webapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI_APPLICATION = 'webapp.wsgi.application' # BB: Not needed since we are using as ASGI!
ASGI_APPLICATION = 'webapp.asgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'PAGE_SIZE': 50,
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            'hosts': [REDIS_URL],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': DB_HOST, 
        'PORT': DB_PORT, 
        'NAME': DB_NAME,
        'USER': DB_USER, 
        'PASSWORD': DB_PASSWORD,
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },

    'handlers': {
        'backend_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'webapp_backend.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'webapp': {
            'handlers': ['backend_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = []  # optional, usually empty
STATIC_ROOT = BASE_DIR / 'staticfiles'  # for collectstatic

# Who emails are sent from
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
