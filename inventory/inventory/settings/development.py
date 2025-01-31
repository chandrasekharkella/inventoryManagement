import datetime
import os
import pathlib

# from medicalShare.settings.base import *
from inventory.settings.base import *

from inventory.settings.base import SIMPLE_JWT

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test1',
        'USER': 'root',
        'PASSWORD':'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


# EMAIL_BACKEND = 'django_ses.SESBackend'
# EMAIL_HOST = "shareitems.in"
# EMAIL_PORT = "465"
# EMAIL_HOST_USER = "noreply@shareitems.in"
# EMAIL_HOST_PASSWORD = "castus1@3"
# EMAIL_USE_TLS = True

EMAIL_BACKEND = 'django_ses.SESBackend'
EMAIL_HOST = "shareitems.in"
EMAIL_PORT = "465"
EMAIL_HOST_USER = "noreply@shareitems.in"
EMAIL_HOST_PASSWORD = "castus1@3"
EMAIL_USE_TLS = True
ADMIN_EMAIL = "chandrasekharkella16@gmai.com"

AWS_ACCESS_KEY_ID = 'AKIAY2USVhjkjhjHXV75ANNKZ6'
AWS_SECRET_ACCESS_KEY = 'mouYgcOihLUxoC0hjjhhjbGl3ghropVsI+eZaxOnTctPhZI'


SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=7)})

# file dir
MEDIA_URL = '/home/devshareitems/devshareitemsapi/'
MEDIA_ROOT = '/home/devshareitems/devshareitemsapi/'

# web url
WEB_HOST_URL = 'https://abcd.com/'
API_HOST_URL = 'https://abcd.com/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'api.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}



REQUEST_LOGGING_ENABLE_COLORIZE = False
REQUEST_LOGGING_SENSITIVE_HEADERS = ['HTTP_AUTHORIZATION', 'HTTP_USER_AGENT', 'X-Page-Generation-Duration-ms']

JWT_SECRECT_KEY = 'CASTUSinfoPVT1@3DEVRENTAL'
JWT_ALGO = 'HS256'
WEBHOOK_URL="http://127.0.0.1:8000/api/webhook"
endpoint_secret = 'whsec_oHgSUpZgdoXaaWFI34PB5RkT5YqCpPPm'

#endpoint_secret = 'whsec_Q2TbmOS4a1gFPSwucJxpqQKEYes3jV5s'
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']  # Important for JSON payloads

CELERY_WEBHOOK_MAX_RETRIES = 5  # Maximum retry attempts
CELERY_WEBHOOK_INITIAL_RETRY_DELAY = 1  # Initial delay before the first retry (seconds)
CELERY_WEBHOOK_TIMEOUT = 10 # Timeout for webhook requests (seconds)