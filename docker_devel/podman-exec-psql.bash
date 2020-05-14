#!/bin/bash

PODMAN_ID="$(podman ps --format='{{.ID}}' --filter name=test_postgres | head -n 1)"

if [ -z "${PODMAN_ID}" ]; then
    echo "Container not running";
else
    podman exec -u postgres -ti "${PODMAN_ID}" psql -d fileIndexer
fi