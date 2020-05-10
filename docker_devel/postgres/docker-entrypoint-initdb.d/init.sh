#!/bin/bash
set -e

export APP_DB_NAME="fileIndexer"
export SCHEMAS="core
video
audio"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE "${APP_DB_NAME}";
EOSQL

for SCHEMA in SCHEMAS; do
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${APP_DB_NAME}" <<-EOSQL
        CREATE SCHEMA "${SCHEMA}";
EOSQL
done