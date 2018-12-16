# Setlist Spy
Setlist Spy is an API for searching DJ setlists to discover new music. Other music suggestion engines like Youtube tend to create feedback loops by overrelying on what else you have already played or what else other people who play the same music also play. In contrast, Setlist Spy lets you pick the minds of cratediggers to find new musical inspiration.

### Features
- Django 2.0 / Rest Framework API
- PostgreSQL 9.6
- Redis Cache
- Dataset Built from [MixesDB.com](http://mixesdb.com) XML Dumps
- Celery, Flower for Sanitizing Data and Seeding the DB -- [flower.setlistspy.com](http://flower.setlistspy.com)
- [Silk](https://github.com/jazzband/django-silk) for Query Monitoring / Tuning
- React Frontend: [coreybobco/setlistspy-web](https://github.com/coreybobco/setlistspy-web)
- Kubernetes Deployment for Google Cloud Platform

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
./manage.py scrape_mixesdb.py
``` 

### Kubernetes
In .config/gcloud/secrets, store your environment variables in cloudsql.txt and django.txt

### Roadmap Features
- Celery Beat for Continuous Updates to Dataset
- API Call for "Most Similar DJ" based on number of tracks / artist / label plays shared
- Music Suggestion Searches for Genres Based on DJ/Artist Genre Affiliations Pulled from Discogs API
- "Markov Chain" DJ Setlist