#! /usr/bin/env bash

docker-compose -f local.yml run --rm app ./manage.py test --settings=config.settings.test "$@"