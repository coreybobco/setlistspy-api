FROM python:3.6.9-alpine

RUN mkdir -p /usr/src/app

RUN apk add --no-cache --virtual .build-deps \
    bash \
    gcc \
    py3-gevent \
    python3-dev \
    libxslt-dev \
    musl-dev \
    postgresql-dev \
    && python3 -m pip install --no-cache-dir psycopg2

WORKDIR /usr/src/app/
RUN mkdir /usr/src/app/uploads
COPY ./compose/local/django/prepare_db /usr/src/app/prepare_db
COPY ./compose/local/django/entrypoint /usr/src/app/entrypoint
COPY ./compose/local/django/celery/worker/start /usr/src/app/start-celeryworker
COPY ./compose/local/django/celery/beat/start /usr/src/app/start-celerybeat
RUN sed -i 's/\r//' prepare_db && chmod +x prepare_db && \
    sed -i 's/\r//' entrypoint && chmod +x entrypoint && \
    sed -i 's/\r//' start-celeryworker && chmod +x start-celeryworker && \
    sed -i 's/\r//' start-celerybeat && chmod +x start-celerybeat

COPY ./requirements /usr/src/app/requirements
RUN python3 -m pip install --no-cache-dir -r requirements/local.txt

