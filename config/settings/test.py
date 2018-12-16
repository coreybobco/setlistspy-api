from .local import *

DEBUG = False
TEST = True

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# Remove Django toolbar and silk if they are in the middleware and apps
if 'silk.middleware.SilkyMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('silk.middleware.SilkyMiddleware')
    INSTALLED_APPS.remove('silk')
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS.remove('debug_toolbar')

MEDIA_ROOT = 'test_uploads'
