from .base import *

DEBUG = False

SITE_URL = "https://gw-cloud.org"

ALLOWED_HOSTS = ['*']

try:
    from .environment import *
except ImportError:
    pass

