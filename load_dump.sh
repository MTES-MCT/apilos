#!/bin/bash
set -e
tar xzf 20260113004930_apilos_siap_8346.tar.gz

DUMP_FILE=/production/siap/apilos/20260113004930_apilos_siap_8346.pgsql
DB_URL=postgres://apilos:apilos@localhost:5433/apilos

for table in $(psql "${DB_URL}" -t -c "SELECT \"tablename\" FROM pg_tables WHERE schemaname='public'"); do
     psql "${DB_URL}" -c "DROP TABLE IF EXISTS \"${table}\" CASCADE;"
done
pg_restore -d "${DB_URL}" --clean --no-acl --no-owner --no-privileges "${DUMP_FILE}"