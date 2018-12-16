#!/bin/sh
set -e

# General postgresql tweaks
sed -i 's/#logging_collector = off/logging_collector = on/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#log_min_duration_statement = -1/log_min_duration_statement = 10/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#checkpoint_completion_target = .5/checkpoint_completion_target = .7/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#wal_buffers = -1/wal_buffers = 16MB/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#random_page_cost = 4.0/random_page_cost = 1.1/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#effective_io_concurrency = 1/effective_io_concurrency = 200/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#min_wal_size = 80MB/min_wal_size = 1GB/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#max_wal_size = 1GB/max_wal_size = 2GB/g' /var/lib/postgresql/data/postgresql.conf

# Specific to ram size
sed -i 's/#shared_buffers = 128MB/shared_buffers = 4GB/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#work_mem = 4MB/work_mem = 20971kB/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#effective_cache_size = 4GB/effective_cache_size = 12GB/g' /var/lib/postgresql/data/postgresql.conf
sed -i 's/#maintenance_work_mem = 64MB/maintenance_work_mem = 1GB/g' /var/lib/postgresql/data/postgresql.conf

# Perform all actions as $POSTGRES_USER
export PGUSER="$POSTGRES_USER"

{
for DB in public "$POSTGRES_DB"; do
	echo "Loading PostGIS extensions into $DB"
	"${psql[@]}" --dbname="$DB" <<-'EOSQL'
		CREATE EXTENSION IF NOT EXISTS hypopg
EOSQL
done
} || true