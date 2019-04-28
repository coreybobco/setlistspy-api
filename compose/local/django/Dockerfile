FROM python:3.6.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update \
  && apt-get install -y postgresql-client

COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/local.txt

COPY config /usr/src/app/config
COPY ./gunicorn_config.py ./manage.py /usr/src/app/

COPY setlistspy /usr/src/app/setlistspy
COPY ./lib /usr/src/app/lib

COPY ./compose/local/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r//' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r//' /start-celerybeat
RUN chmod +x /start-celerybeat

RUN mkdir /usr/src/app/uploads