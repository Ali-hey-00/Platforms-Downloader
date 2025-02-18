import os
from celery import Celery
from django.conf import settings
from celery.signals import setup_logging

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('instagram_downloader')

# Config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered Django apps
app.autodiscover_tasks()

# Configure Celery
app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    
    # Queue settings
    task_queues={
        'downloads': {
            'exchange': 'downloads',
            'routing_key': 'downloads',
            'queue_arguments': {'x-max-priority': 10}
        },
        'default': {
            'exchange': 'default',
            'routing_key': 'default'
        }
    },
    
    # Task execution settings
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_backend='django-db',
    result_expires=3600,  # 1 hour
    
    # Rate limiting
    task_annotations={
        'downloader.tasks.process_download': {
            'rate_limit': '10/m'
        }
    },
    
    # Error handling
    task_routes={
        'downloader.tasks.process_download': {
            'queue': 'downloads'
        }
    }
)

@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure Celery logging"""
    from logging.config import dictConfig
    from django.conf import settings
    
    dictConfig(settings.LOGGING)