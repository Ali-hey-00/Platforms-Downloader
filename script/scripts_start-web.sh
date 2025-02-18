#!/bin/sh
set -e

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-4} \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-tmp-dir /dev/shm \
    --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
    --max-requests-jitter 50 \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --keep-alive 75 \
    --access-logfile - \
    --error-logfile - \
    --log-level info