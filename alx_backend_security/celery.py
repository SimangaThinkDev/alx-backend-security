# alx_backend_security/celery.py

import os
from celery import Celery

# Set default Django settings module for 'celery' command-line program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_security.settings')

app = Celery('alx_backend_security')

# Load settings from Django settings, using the `CELERY_` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django app configs
app.autodiscover_tasks()
