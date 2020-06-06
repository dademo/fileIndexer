#!/bin/bash

SCRIPT_PATH="$(dirname $0)"
source "${SCRIPT_PATH}/config.bash"

set -o xtrace

${DOCKER_CMD} build -t postgres-test "${SCRIPT_PATH}/postgres"

${DOCKER_CMD} run \
    --rm \
    --name test_postgres \
    --env POSTGRES_PASSWORD=postgres \
    --publish 5432:5432 \
    --detach \
    postgres-test
