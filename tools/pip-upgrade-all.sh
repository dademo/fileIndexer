#!/bin/bash

if [ -z "${VIRTUAL_ENV}" ]; then
    echo "You must be inside a virtualenv to launch this script"
    exit 1
fi

python -m pip install --upgrade pip
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -r -n1 pip install -U