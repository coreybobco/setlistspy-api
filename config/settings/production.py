from .base import *  # noqa
from .base import env

SECRET_KEY = env('DJANGO_SECRET_KEY')

DEBUG = False

# ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['setlistspy.com'])
ALLOWED_HOSTS = ['*']
STATIC_URL = env('STATIC_URL')
