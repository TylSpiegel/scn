from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = os.getenv('ENV_ALLOWED_HOSTS').split(',')

try:
    from .local import *
except ImportError:
    pass
