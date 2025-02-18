#!/bin/sh
set -e

echo "Starting Celery worker..."
exec celery -A core worker \
    --loglevel=info \
    --concurrency=${CELERY_WORKERS:-4} \
    --max-tasks-per-child=${CELERY_MAX_TASKS_PER_CHILD:-100}