from __future__ import absolute_import

from celery.schedules import crontab
from celery import Celery

import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

app = Celery('src')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.broker_url = 'redis://redis:6379/0'


app.conf.beat_schedule = {
    'refresh_locations': {
        'task': 'api.tasks.update_all_cars_locations',
        'schedule': crontab(minute='*/1'),
    },
}
app.conf.timezone = 'UTC'