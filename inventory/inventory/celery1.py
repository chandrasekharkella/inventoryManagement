import os
from celery import Celery

# Set the default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings.development')

# Create a single Celery instance
app = Celery('inventory')

# Add the setting to avoid the deprecation warning
app.conf.broker_connection_retry_on_startup = True  # New setting for Celery 6.0 and above

# # Configure Celery to use Redis as the broker and result backend
app.conf.broker_url = 'redis://localhost:6379'
app.conf.result_backend = 'redis://localhost:6379'
# app = Celery('inventory', 
#              broker='amqp://guest:guest@localhost:5672//',
#              backend='rpc://')
# Namespace='CELERY' means all celery-related settings in Django settings should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all registered Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
