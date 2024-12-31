from .base import *
import os

DEBUG = False

SECRET_KEY = os.getenv('ENV_SECRET_KEY')

ALLOWED_HOSTS = os.getenv('ENV_ALLOWED_HOSTS').split(',')
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'verbose',
        },
        'file_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug_info.log',
            'formatter': 'simple',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file_debug', 'file_info', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'wagtail': {
            'handlers': ['file_debug', 'file_info', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

try:
    from .local import *
except ImportError:
    pass
