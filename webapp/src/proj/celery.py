from celery.schedules import crontab
from celery import Celery
import proj.tasks

import os


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

app = Celery('proj')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'refresh_locations': {
        'task': 'proj.tasks.update_all_cars_locations',
        'schedule': crontab(minute='*/3'),
    },
}