#!/bin/bash

echo "Apply database migrations"
# python3 manage.py migrate

# echo "Apply database migrations"
# python3 manage.py loaddata streams.yaml

# echo "Starting server"
# python3 manage.py runserver 0.0.0.0:8000

exec "$@"