from .base import *

INSTALLED_APPS += ('corsheaders', )
CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE.append('corsheaders.middleware.CorsMiddleware')

SITE_URL = "http://localhost:3002"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    }
}

try:
    from .local import *
except:
    pass
