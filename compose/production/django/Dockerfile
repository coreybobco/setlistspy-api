FROM python:3.6.6

RUN mkdir -p /usr/src/app

RUN apt-get update \
  && apt-get install -y postgresql-client git

#RUN groupadd -r django \
#    && useradd -r -g django django

WORKDIR /usr/src/
RUN git clone https://github.com/coreybobco/setlistspy-api.git

WORKDIR /usr/src/setlistspy-api/
COPY ./requirements /usr/src/app/requirements
COPY config /usr/src/app/config
COPY ./gunicorn_config.py ./manage.py /usr/src/app/
COPY setlistspy /usr/src/app/setlistspy
COPY ./lib /usr/src/app/lib
COPY ./compose/local/django/prepare_db /usr/src/app/prepare_db
COPY ./compose/local/django/entrypoint /usr/src/app/entrypoint
COPY ./compose/production/django/start /usr/src/app/start
COPY ./compose/local/django/celery/worker/start /usr/src/app/start-celeryworker
COPY ./compose/local/django/celery/beat/start /usr/src/app/start-celerybeat
COPY ./compose/local/django/celery/flower/start /usr/src/app/start-flower

WORKDIR /usr/src/app/
RUN sed -i 's/\r//' prepare_db
RUN chmod +x prepare_db
RUN sed -i 's/\r//' entrypoint
RUN chmod +x entrypoint
RUN sed -i 's/\r//' start
RUN chmod +x start
RUN sed -i 's/\r//' start-celeryworker
RUN chmod +x start-celeryworker
RUN sed -i 's/\r//' start-celerybeat
RUN chmod +x start-celerybeat
RUN sed -i 's/\r//' start-flower
RUN chmod +x start-flower

RUN pip install --no-cache-dir -r requirements/production.txt
RUN mkdir /usr/src/app/uploads