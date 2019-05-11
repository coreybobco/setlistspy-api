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

COPY ./compose/local/django/prepare_db prepare_db
COPY ./compose/local/django/entrypoint entrypoint
COPY ./compose/local/django/celery/worker/start start-celeryworker
COPY ./compose/local/django/celery/beat/start start-celerybeat

WORKDIR /usr/src/app/
RUN sed -i 's/\r//' prepare_db && chmod +x prepare_db && \
    sed -i 's/\r//' entrypoint && chmod +x entrypoint && \
    sed -i 's/\r//' start-celeryworker && chmod +x start-celeryworker && \
    sed -i 's/\r//' start-celerybeat && chmod +x start-celerybeat

RUN mkdir /usr/src/app/uploads