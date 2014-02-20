from .common import *

import os

DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = [
        os.environ['AMBER_ALLOWED_HOST'],
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['AMBER_SECRET_KEY']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['AMBER_DB_NAME'],
        'USER': os.environ['AMBER_DB_USER'],
        'PASS': os.environ.get('AMBER_DB_PASS'),
        'HOST': os.environ.get('AMBER_DB_HOST', ''),
        'PORT': os.environ.get('AMBER_DB_PORT', '5432'),
    },
}
