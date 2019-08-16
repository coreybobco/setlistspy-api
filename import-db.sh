#!/usr/bin/env bash
if [[ "$1" = "" ]]; then
    echo "Requires one argument:"
    echo "- database filename"
    exit
fi
echo "Copying database to postgresql instance"
docker cp "${1}" $(docker ps --filter="label=postgresql" -aq):/home/db
echo "..Done"
docker exec $(docker ps --filter="label=postgresql" -aq) su postgres sh -c "psql setlistspy < /home/db"
echo "Importing db... (may take some time)"
docker exec $(docker ps --filter="label=postgresql" -aq) rm /home/db
echo "Done"