#! /usr/bin/env bash

docker-compose run --rm app ./manage.py test --settings=setlistspy.test_settings "$@"
