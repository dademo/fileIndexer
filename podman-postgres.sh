#!/bin/sh

podman run --rm --name test_postgres -e POSTGRES_PASSWORD=postgres -p5432:5432 -d postgres
