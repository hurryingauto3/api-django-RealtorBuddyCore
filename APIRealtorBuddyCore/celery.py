import os
from celery import Celery
from celery.schedules import crontab
from .config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'APIRealtorBuddyCore.settings')

app = Celery('APIRealtorBuddyCore')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Update the Celery configuration with the custom settings
app.conf.update(
    BROKER_URL=CELERY_BROKER_URL,
    RESULT_BACKEND=CELERY_RESULT_BACKEND,
    ACCEPT_CONTENT=['json'],
    TASK_SERIALIZER='json',
    RESULT_SERIALIZER='json',
    BEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler',
)
app.conf.broker_connection_retry_on_startup = True
app.conf.broker_connection_max_retries = 10
app.conf.broker_connection_timeout = 10


