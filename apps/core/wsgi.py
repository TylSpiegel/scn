"""
WSGI config for website project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the Django settings module path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.core.settings.dev")

application = get_wsgi_application()
