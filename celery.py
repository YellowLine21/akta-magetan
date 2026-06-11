import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'akta_magetan.settings')

app = Celery('akta_magetan')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
