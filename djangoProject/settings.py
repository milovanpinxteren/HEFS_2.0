"""
Django settings for djangoProject project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()
SHOPIFY_ACCESS_TOKEN = env('SHOPIFY_ACCESS_TOKEN')
GERIJPTEBIEREN_ACCESS_TOKEN = env('GERIJPTEBIEREN_ACCESS_TOKEN')
GEREIFTEBIERE_ACCESS_TOKEN = env('GEREIFTEBIERE_ACCESS_TOKEN')
HOB_ACCESS_TOKEN = env('HOB_ACCESS_TOKEN')
MICROCASH_FTP_PASSWORD = env('MICROCASH_FTP_PASSWORD')
SCHEDULE_INTERVAL = env('SCHEDULE_INTERVAL')
PAASONTBIJT_ACCESS_TOKEN = env('PAASONTBIJT_ACCESS_TOKEN')
KERSTDINER_ACCESS_TOKEN = env('KERSTDINER_ACCESS_TOKEN')
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-tzuj9rtn&b0&uyhh@8mqhd#%g338+9cicqittsu2#j8c=eopyb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['hefs.89.145.161.168.sslip.io', '127.0.0.1', 'localhost', 'hefs.nl', 'www.hefs.nl', '89.145.161.168']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hefs.apps.HighendfoodsolutionsConfig',
    'django_pivot',
    'mathfilters',
    'django_rq',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangoProject.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hefs',

        'USER': 'postgres',

        'PASSWORD': 'postgres',

        'HOST': 'localhost',

        'PORT': '5432',
    }
}

import dj_database_url

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# LOGIN_REDIRECT_URL = '/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
full_sync = 'high'
small_sync = 'low'

RQ_QUEUES = {
    'default': {
        'URL': redis_url,
        'DEFAULT_TIMEOUT': os.getenv('REDIS_TIMEOUT', 7200),
    },
    full_sync: {
        'URL': redis_url,
        'DEFAULT_TIMEOUT': os.getenv('REDIS_TIMEOUT', 7200),
    },
    small_sync: {
        'URL': redis_url,
        'DEFAULT_TIMEOUT': os.getenv('REDIS_TIMEOUT', 7200),

    }
}
