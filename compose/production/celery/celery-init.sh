#!/bin/bash
for i in $(seq 1 $(expr $num_workers))
do
    celery multi start worker"$i" --detach -A setlistspy --loglevel=info -Q "$queues" --concurrency=10 -n "celery" --pidfile=/tmp/"$i".pid
    celery multi restart worker"$i" --detach -A setlistspy --loglevel=info --concurrency=10 -n "celery" --pidfile=/tmp/"$i".pid
done
sleep infinity