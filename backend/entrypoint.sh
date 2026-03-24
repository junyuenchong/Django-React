#!/bin/sh
# Wait for the database and run migrations with retry.
MAX_RETRIES="${DB_MIGRATE_MAX_RETRIES:-30}"
SLEEP_SECONDS="${DB_MIGRATE_RETRY_DELAY_SECONDS:-2}"
ATTEMPT=1

echo "Running migrations (with retry)..."
while [ "$ATTEMPT" -le "$MAX_RETRIES" ]; do
  if python manage.py migrate --noinput; then
    echo "Migrations applied successfully."
    break
  fi

  echo "Migration attempt ${ATTEMPT}/${MAX_RETRIES} failed. Retrying in ${SLEEP_SECONDS}s..."
  ATTEMPT=$((ATTEMPT + 1))
  sleep "$SLEEP_SECONDS"
done

if [ "$ATTEMPT" -gt "$MAX_RETRIES" ]; then
  echo "Migrations failed after ${MAX_RETRIES} attempts. Exiting."
  exit 1
fi

echo "Starting Django..."
# Gunicorn serves the API over 8000 inside the container.
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-2}"

