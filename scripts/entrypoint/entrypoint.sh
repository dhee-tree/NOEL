#!/bin/sh

# Stop on error
set -e

# 1. Collect static files to the shared volume
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 2. Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# 3. Start Gunicorn
echo "Starting Gunicorn..."
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 noelProject.wsgi:application
