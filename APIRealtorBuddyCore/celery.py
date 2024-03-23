import os
from celery import Celery
from celery.schedules import crontab

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
    ACCEPT_CONTENT=['json'],
    TASK_SERIALIZER='json',
    RESULT_SERIALIZER='json',
)
app.conf.broker_connection_retry_on_startup = True
app.conf.broker_connection_max_retries = 10
app.conf.broker_connection_timeout = 10

app.conf.beat_schedule = {
    # 'run-my_periodic_task-every-minute': {
    #     'task': 'mayAIService.tasks.async_processMessages',
    #     'schedule': crontab(minute='*/1', hour='13-23'),
    # },
    # 'run-my_periodic_task-every-ten-minutes': {
    #     'task': 'leadProcessingService.tasks.processLeadsForOutreach',
    #     'args': (30,),  # This is the limit of leads to process
    #     'schedule': crontab(minute='*/10', hour='13-23'),
    # },
    # You can add more tasks to the schedule dictionary as needed.
}