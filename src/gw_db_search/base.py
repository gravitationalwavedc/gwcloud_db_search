"""
Django settings for gwcloud_auth project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^zzul@u)rxayk67^%3kf^59!pw&-vfv0lnv6#6h)w6!eyjzz!g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'db_search.apps.DbSearchConfig',
    'graphene_django',
    'django_jenkins'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'querycount.middleware.QueryCountMiddleware'
]

ROOT_URLCONF = 'gw_db_search.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'gw_db_search.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASE_ROUTERS = ['db_search.utils.db_router.DBRouter']

mysql_host = os.environ.get('MYSQL_HOST', 'localhost')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3'
    },
    'gwauth': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gwcloud_auth',
        'HOST': mysql_host,
        'USER': 'root',
        'PORT': 3306,
        'PASSWORD': 'root',
        'TEST': {
            'NAME': 'test_gwcloud_auth',
        },
    },
    'jobserver': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gwcloud_jobcontroller',
        'HOST': mysql_host,
        'USER': 'root',
        'PORT': 3306,
        'PASSWORD': 'root',
        'TEST': {
            'NAME': 'test_gwcloud_jobcontroller',
        },
    },
    'bilbyui': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gwcloud_bilby',
        'HOST': mysql_host,
        'USER': 'root',
        'PORT': 3306,
        'PASSWORD': 'root',
        'TEST': {
            'NAME': 'test_gwcloud_bilby',
        },
    },
    'viterbi': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gwlab_viterbi',
        'HOST': mysql_host,
        'USER': 'root',
        'PORT': 3306,
        'PASSWORD': 'root',
        'TEST': {
            'NAME': 'test_gwlab_viterbi',
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Only used in development for serving graphql.js
STATIC_URL = '/static/'

GRAPHENE = {
    'SCHEMA': 'gw_db_search.schema.schema',
    'SCHEMA_INDENT': 2,  # Defaults to None (displays all data on a single line),
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]


def jwt_get_user_by_payload_override(payload):
    from .jwt_tools import jwt_get_user_by_payload
    return jwt_get_user_by_payload(payload)


GRAPHQL_JWT = {
    # Our implementation of JWT_PAYLOAD_GET_USERNAME_HANDLER returns a full user object rather than just a username
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': jwt_get_user_by_payload_override,
    # Internally this usually takes a username returned by JWT_PAYLOAD_GET_USERNAME_HANDLER, but as we're returning
    # the full user object from JWT_PAYLOAD_GET_USERNAME_HANDLER, we don't do any processing, and simply just return
    # the passed user object.
    'JWT_GET_USER_BY_NATURAL_KEY_HANDLER': lambda x: x,
    'JWT_VERIFY_EXPIRATION': True
}

AUTH_USER_MODEL = 'gwauth.GWCloudUser'

GWCLOUD_APPS = {
    'gwauth': 'apps/gwcloud_auth/src/',
    'jobserver': 'apps/gwcloud_job_server/src/utils/schema/',
    'bilbyui': 'apps/gwcloud_bilby/src/',
    'viterbi': 'apps/gwlab_viterbi/src/'
}

for module, path in GWCLOUD_APPS.items():
    sys.path.append(path)
    INSTALLED_APPS.append(module)

TESTING = False

# The maximum number of results to return from the graphql endpoint
GRAPHENE_RESULTS_LIMIT = 100

EMBARGO_START_TIME = None
