from celery import shared_task, Task
from django.db import transaction, DEFAULT_DB_ALIAS


class CeleryAtomic(transaction.Atomic):
    def __enter__(self, *args, **kwargs):
        connection = transaction.get_connection(self.using)
        connection._setlistspy_celery_atomic = True
        if not hasattr(connection, '_setlistspy_celery_on_commit'):
            connection._setlistspy_celery_on_commit = []
        connection._setlistspy_celery_on_commit.append([])
        super().__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        super().__exit__(*args, **kwargs)
        connection = transaction.get_connection(self.using)
        try:
            for func in connection._setlistspy_celery_on_commit.pop():
                func()
        finally:
            if not connection._setlistspy_celery_on_commit:
                connection._setlistspy_celery_atomic = False


# https://medium.com/hypertrack/dealing-with-database-transactions-in-django-celery-eac351d52f5f
class TransactionAwareTask(Task):
    '''
    Task class which is aware of django db transactions and only executes tasks
    after transaction has been committed
    '''
    abstract = True

    def apply_async(self, *args, **kwargs):
        '''
        Unlike the default task in celery, this task does not return an async
        result
        '''
        connection = transaction.get_connection()
        if getattr(connection, '_setlistspy_celery_atomic', False):
            connection._setlistspy_celery_on_commit[-1].append(
                lambda: super(TransactionAwareTask, self).apply_async(*args, **kwargs),
            )
        else:
            return super().apply_async(*args, **kwargs)


shared_task = shared_task(base=TransactionAwareTask)
