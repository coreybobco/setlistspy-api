
import os
from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings


if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')  # pragma: no cover

celery_config = {
    'task_serializer': 'json',
    'broker_url': settings.BROKER_URL,
    'result_backend': settings.BROKER_URL,
    'task_routes': {
        'setlistspy.tasks.mixesdb': {'queue': 'celery'},
        'setlistspy.tasks.*':  {'queue': 'celery'},
    }
}

app = Celery('setlistspy')
# Using a string here means the worker will not have to
# pickle the object when using Windows.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(celery_config) #'django.conf:settings', namespace='CELERY')


class CeleryAppConfig(AppConfig):
    name = 'setlistspy.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)