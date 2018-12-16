from .base import *  # noqa
from .base import env
# import dj_database_url

SECRET_KEY = env('DJANGO_SECRET_KEY', default='7BuURoRA0FIaBFlFw0K6JdwcGG9nEWU7qhg8mdawtB8OA3AiSe2LO8yDGPo073Ah')
ALLOWED_HOSTS = ['*']

DEBUG = True

# DATABASES['default'] = dj_database_url.config(
#     default='postgres://127.0.0.1:5432/setlistspy'
# )

MIDDLEWARE.insert(3, 'silk.middleware.SilkyMiddleware')
INSTALLED_APPS.append('silk')
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_PYTHON_PROFILER_RESULT_PATH = 'profile_data/'

STATIC_URL = '/static/'

import sys

def myexcepthook(*args, **kwargs):
    import traceback
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import TerminalFormatter

    tbtext = ''.join(traceback.format_exception(*args, **kwargs))
    lexer = get_lexer_by_name('pytb', stripall=True)
    formatter = TerminalFormatter()
    sys.stderr.write(highlight(tbtext, lexer, formatter))

sys.excepthook = myexcepthook