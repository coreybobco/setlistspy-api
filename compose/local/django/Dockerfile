FROM python:3.6.6

RUN mkdir -p /usr/src/app

RUN apt-get update \
  && apt-get install -y postgresql-client git

WORKDIR /usr/src/app/
COPY ./requirements /usr/src/app/requirements
RUN pip install --no-cache-dir -r requirements/local.txt
RUN mkdir /usr/src/app/uploads