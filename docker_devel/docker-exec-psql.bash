#!/bin/bash

source "$(dirname $0)/config.bash"

CONTAINER_ID="$(${DOCKER_CMD} ps --format='{{.ID}}' --filter name=test_postgres | head -n 1)"

if [ -z "${CONTAINER_ID}" ]; then
    echo "Container not running";
else
    ${DOCKER_CMD} exec -u postgres -ti "${CONTAINER_ID}" psql -d fileIndexer
fi