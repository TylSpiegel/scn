from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Override WAGTAILADMIN_BASE_URL from env
WAGTAILADMIN_BASE_URL = os.getenv('WAGTAILADMIN_BASE_URL', 'http://localhost:8000')

try:
    from .local import *
except ImportError:
    pass
