#!/bin/sh

SCRIPT_PATH="$(dirname $0)"

DB_NAME="fileIndexer"
DB_SCHEMAS="core"

#    --volume ./docker-entrypoint-initdb.d:/docker-entrypoint-initdb.d:ro \

set -o xtrace

podman build -t postgres-test "${SCRIPT_PATH}/postgres"

podman run \
    --rm \
    --name test_postgres \
    --env POSTGRES_PASSWORD=postgres \
    --publish 5432:5432 \
    --detach \
    postgres-test

#podman exec -i $PODMAN_ID /bin/sh << EOF
#    su -c psql <<< "CREATE DATABASE ${DB_NAME}" postgres
#EOF

#for SCHEMA in DB_SCHEMAS; do
#    podman exec -i $PODMAN_ID /bin/sh << EOF
#        su -c psql --dbname "${DB_NAME}" <<< "CREATE SCHEMA ${SCHEMA}" postgres
#EOF
#done
