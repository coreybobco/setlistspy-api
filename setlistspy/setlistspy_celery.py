from __future__ import absolute_import
import os
import xmltodict

from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

celery_config = {
    'task_serializer': 'json',
    'broker_url': settings.BROKER_URL,
    'result_backend': settings.BROKER_URL,
    'task_routes': {
        'setlistspy.tasks.mixesdb': {'queue': 'celery'},
        'setlistspy.tasks.*':  {'queue': 'celery'},
    }
}


# if settings.TEST:  # or settings.DEBUG: #-- Uncomment this to execute Celery tasks in view
#     celery_config['broker_transport'] = 'memory'
#     celery_config['task_always_eager'] = True
#     celery_config['task_eager_propagates'] = True

app = Celery('setlistspy')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object(celery_config)
app.autodiscover_tasks()
