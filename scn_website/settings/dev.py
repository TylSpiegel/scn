from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

# CSRF trusted origins (needed when testing custom hostnames locally).
# Default: derived from the allowed hosts as http; overridable via env.
_csrf_env = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '')
if _csrf_env:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_env.split(',') if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [f"http://{h}" for h in ALLOWED_HOSTS if not h.startswith('.')]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Override WAGTAILADMIN_BASE_URL from env
WAGTAILADMIN_BASE_URL = os.getenv('WAGTAILADMIN_BASE_URL', 'http://localhost:8000')

try:
    from .local import *
except ImportError:
    pass
