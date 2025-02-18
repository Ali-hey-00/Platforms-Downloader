import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_downloader.settings')

# Create celery app
app = Celery('instagram_downloader')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configure Celery
app.conf.update(
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    task_ignore_result=True,
    task_store_errors_even_if_ignored=True,
    task_remote_tracebacks=True,
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    task_queues={
        'default': {
            'exchange': 'default',
            'routing_key': 'default',
        },
        'downloads': {
            'exchange': 'downloads',
            'routing_key': 'downloads',
        },
    },
    task_routes={
        'downloader.tasks.*': {
            'queue': 'downloads',
            'exchange': 'downloads',
            'routing_key': 'downloads',
        },
    },
    broker_transport_options={
        'visibility_timeout': 3600,  # 1 hour
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.5,
    },
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Auto-discover tasks in all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')