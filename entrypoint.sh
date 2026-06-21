#!/bin/bash
set -e

mkdir -p output
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
