import os

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

SECRET_KEY = os.getenv('DB_SEARCH_SECRET_KEY', 'super_secret')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3'
    },
    'gwauth': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gwcloud_auth',
        'HOST': MYSQL_HOST,
        'USER': MYSQL_USER,
        'PORT': 3306,
        'PASSWORD': MYSQL_PASSWORD,
    },
    'jobserver': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gwcloud_jobcontroller',
        'HOST': MYSQL_HOST,
        'USER': MYSQL_USER,
        'PORT': 3306,
        'PASSWORD': MYSQL_PASSWORD,
    },
    'bilbyui': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gwcloud_bilby',
        'HOST': MYSQL_HOST,
        'USER': MYSQL_USER,
        'PORT': 3306,
        'PASSWORD': MYSQL_PASSWORD,
    },
    'viterbi': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gwlab_viterbi',
        'HOST': MYSQL_HOST,
        'USER': MYSQL_USER,
        'PORT': 3306,
        'PASSWORD': MYSQL_PASSWORD,
    },
}
