#!/bin/bash

set -e
set -u

# System configuration
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -c "alter system set listen_addresses='*';"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -c "alter system set shared_buffers='256MB';"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -c "alter system set max_connections=200;"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -c "alter system set work_mem='256MB';"

# Ecoloweb

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
create database ecoloweb;
create database ecolotest;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname ecolotest <<-EOSQL
create schema if not exists ecolo;
EOSQL
