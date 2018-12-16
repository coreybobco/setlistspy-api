from .mixesdb import *

from celery.signals import task_failure


def celery_base_data_hook(request, data):
    data['framework'] = 'celery'

