#!/bin/bash

SCRIPT_PATH="$(dirname $0)"
source "${SCRIPT_PATH}/config.bash"

set -o xtrace

${DOCKER_CMD} build -t postgres-test "${SCRIPT_PATH}/postgres"

# Checking for volume
if [ -z "$(${DOCKER_CMD} volume ls -f name=postgres-test-volume --format '{{.Name}}')" ]; then
    ${DOCKER_CMD} volume create postgres-test-volume
fi

${DOCKER_CMD} run \
    --rm \
    --name test_postgres \
    --env POSTGRES_PASSWORD=postgres \
    --volume postgres-test-volume:/var/lib/postgresql/data:rw \
    --publish 5432:5432 \
    --detach \
    postgres-test

