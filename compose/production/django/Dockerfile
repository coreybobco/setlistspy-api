FROM python:3.6.6

RUN mkdir -p /usr/src/app

RUN apt-get update \
  && apt-get install -y postgresql-client git

WORKDIR /usr/src/app/
RUN git clone https://github.com/coreybobco/setlistspy-api.git .

COPY ./compose/local/django/prepare_db /usr/src/app/prepare_db
COPY ./compose/local/django/entrypoint /usr/src/app/entrypoint
COPY ./compose/production/django/start /usr/src/app/start
COPY ./compose/local/django/celery/worker/start /usr/src/app/start-celeryworker
COPY ./compose/local/django/celery/beat/start /usr/src/app/start-celerybeat

WORKDIR /usr/src/app/
RUN sed -i 's/\r//' prepare_db && chmod +x prepare_db && \
    sed -i 's/\r//' entrypoint && chmod +x entrypoint && \
    sed -i 's/\r//' start && chmod +x start && \
    sed -i 's/\r//' start-celeryworker && chmod +x start-celeryworker && \
    sed -i 's/\r//' start-celerybeat && chmod +x start-celerybeat

COPY ./requirements /usr/src/app/requirements
RUN pip install --no-cache-dir -r requirements/production.txt
RUN mkdir /usr/src/app/uploads