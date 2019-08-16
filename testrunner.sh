#! /usr/bin/env bash
echo "Running tests..."
echo "(Try running ./testrunner.sh help to see more options)"
if [[ "$1" = "help" ]]; then
  echo "./testrunner.sh -- runs the test suite"
  echo "./testrunner.sh coveralls -- runs the test suite and submits a report to coveralls.io"
else
  if [[ "$1" = "coveralls" ]]; then
    docker-compose -f local.yml run --rm app bash -c "./manage.py test --settings=config.settings.test "$@" && coveralls"
  else
    docker-compose -f local.yml run --rm app ./manage.py test --settings=config.settings.test "$@"
  fi
fi