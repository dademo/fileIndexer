#!/bin/bash

source "$(dirname $0)/config.bash"

${DOCKER_CMD} run \
    --rm \
    -env PGADMIN_DEFAULT_EMAIL=admin@example.com \
    -env PGADMIN_DEFAULT_PASSWORD=postgres \
    --publish 8080:80 \
    --detach \
    dpage/pgadmin4
