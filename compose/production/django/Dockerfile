FROM ubuntu:18.04

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev postgresql-client wget git \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

#RUN groupadd -r django \
#    && useradd -r -g django django

COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt

COPY config /usr/src/app/config
COPY ./gunicorn_config.py ./manage.py /usr/src/app/

COPY setlistspy /usr/src/app/setlistspy
COPY ./lib /usr/src/app/lib

COPY ./compose/local/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint
#RUN chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start
#RUN chown django /start

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r//' /start-celeryworker
RUN chmod +x /start-celeryworker
#RUN chown django /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r//' /start-celerybeat
RUN chmod +x /start-celerybeat
#RUN chown django /start-celerybeat

COPY ./compose/local/django/celery/flower/start /usr/src/app/start-flower
RUN sed -i 's/\r//' /usr/src/app/start-flower
RUN chmod +x /usr/src/app/start-flower

RUN mkdir /usr/src/app/uploads