#!/bin/sh

podman run --rm -e PGADMIN_DEFAULT_EMAIL=admin@example.com -e PGADMIN_DEFAULT_PASSWORD=postgres -p8080:80 -d dpage/pgadmin4
