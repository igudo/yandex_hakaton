# _*_ coding:utf-8 _*_
from .settings import *


# SECURITY
SECRET_KEY = '000000000000000000000000000000000000000000000000000'

# debug mod
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'main.db'),
    }
}



# static
STATIC_ROOT = None
STATICFILES_DIRS = (
  os.path.join(BASE_DIR, 'static'),
)
