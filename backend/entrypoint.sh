#!/bin/sh
# `set -e` can fail on some minimal shells if the script has unexpected
# line-ending/control characters. Keep the entrypoint resilient.

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Django..."
# Gunicorn serves the API over 8000 inside the container.
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-2}"

