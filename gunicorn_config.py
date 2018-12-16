import os

name = 'setlistspy'
worker_class = 'gevent'
worker_connections = 20
max_requests = 100
max_requests_jitter = 50
backlog = 16
port = os.environ.get('PORT', 6400)
bind = [f'0.0.0.0:{port}']
timeout = 28
reload = True
