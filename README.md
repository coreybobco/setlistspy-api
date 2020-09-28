# Setlist Spy

[![Build Status](https://travis-ci.org/coreybobco/setlistspy-api.svg?branch=master)](https://travis-ci.org/coreybobco/setlistspy-api) [![Coverage Status](https://coveralls.io/repos/github/coreybobco/setlistspy-api/badge.svg?branch=master)](https://coveralls.io/github/coreybobco/setlistspy-api?branch=master)

Setlist Spy is an API for searching DJ setlists to discover new music. Other music suggestion engines like Youtube tend to create feedback loops by overrelying on what else you have already played or what else other people who play the same music also play. In contrast, Setlist Spy lets you pick the minds of cratediggers to find new musical inspiration.

### Features
- Django 2.2 + Rest Framework API
- PostgreSQL
- Redis Cache
- Dataset Built from [MixesDB.com](http://mixesdb.com) XML Dumps -- (As of August 2019, Mixesdb.com has removed XML export functionality from their mediawiki, deprecating this information retrieval method.)
- Celery, Flower for Sanitizing Data and Seeding the DB -- [flower.setlistspy.com](http://flower.setlistspy.com:5555)
- [Silk](https://github.com/jazzband/django-silk) for Query Monitoring / Tuning
- React Frontend: [coreybobco/setlistspy-web](https://github.com/coreybobco/setlistspy-web)
- Kubernetes Deployment for Google Cloud Platform
- Travis CI
- Sentry for Error Tracking

There are also a few API calls for statistics I find fascinating but have not had time to implement in the frontend yet.
Here are a few examples:

- Stats for Jeff Mills as a DJ - http://api.setlistspy.com/api/djs/beb0c55f-84fe-4137-bb34-fbce2654a88c/stats/
- Artist Stats for Aphex Twin -- i.e. information on how often tracks by the music artist Aphex Twin have been played in setlists and by what DJs: http://api.setlistspy.com/api/artists/55b11e05-c8e3-43e4-98a7-eb7a1ecff8ae/stats/
- Track Stats for Jeff Mills - The Bells: http://api.setlistspy.com/api/tracks/52c6bceb-c703-41a4-bdd1-b34d5a41e1be/stats/
- Label Stats for Warp Records: http://api.setlistspy.com/api/labels/eeea4fb6-613f-4d34-9a24-41862a3cfc0d/stats/

### Running Locally 
#### ...with Docker
```
docker-compose -f local.yml build
docker-compose -f local.yml up
```
#### ...with Cloud SQL
Place your environment variables in .envs/production/.django and envs/production/.postgres
```
docker-compose -f production.yml build
docker-compose -f production.yml up
```

### Seeding the Database
To populate the database, run:
```
./manage.py scrape_mixesdb --everything
``` 

### Running the Tests
To run the tests, run:
```
./testrunner.sh
``` 
or to run a specific test case, run this, substituting the last part
```
./testrunner.sh setlistspy.app.tests.api.[TEST CASE].[TEST]
``` 

### To import data locally, run
```
./import-db.sh [DB_FILE]
``` 

### Kubernetes
In .config/gcloud/secrets, store your environment variables in cloudsql.txt and django.txt
