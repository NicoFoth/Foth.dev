"""Django settings for foth.dev.

Everything that differs between machines comes from the environment:

    DJANGO_SECRET   the secret key (required)
    DJANGO_DEBUG    "1" on a development machine
    DJANGO_DB_PATH  path of the SQLite database (default: db.sqlite3 next to manage.py)
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET')
DEBUG = os.getenv('DJANGO_DEBUG') == '1'

ALLOWED_HOSTS = ['foth.dev', 'www.foth.dev', 'localhost', '127.0.0.1', '176.9.90.101']

# When TLS ends at the reverse proxy, Django sees plain HTTP and would reject
# every POST from https://foth.dev (login, contact form, puzzle answers, stars)
# in the CSRF origin check.
CSRF_TRUSTED_ORIGINS = ['https://foth.dev', 'https://www.foth.dev']

# Every .dev domain is HTTPS-only (HSTS preload), so cookies never need to
# travel over plain HTTP in production.
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pages',
    'stars',
    'puzzle',
    'projects',
    'csgo',
    'poker',
]

MIDDLEWARE = [
    'pages.middleware.RenderTimeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'stars.middleware.SeenPagesMiddleware',
]

ROOT_URLCONF = 'webservice.urls'
WSGI_APPLICATION = 'webservice.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pages.context_processors.site',
                'stars.context_processors.stars',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.getenv('DJANGO_DB_PATH', BASE_DIR / 'db.sqlite3'),
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Stars and puzzle progress live in the session. Signed cookies keep anonymous
# visitors (and crawlers) from piling up rows in the sessions table.
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 365

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LOGIN_REDIRECT_URL = 'pages:home'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
