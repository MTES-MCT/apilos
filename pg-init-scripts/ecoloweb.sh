#!/bin/bash

set -e
set -u

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
create database ecoloweb;
create database ecolotest;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname ecolotest <<-EOSQL
create schema if not exists ecolo;
EOSQL
