import os
from celery import Celery

# Set default Django settings for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_travel_app.settings")

app = Celery("alx_travel_app")

# Load settings with CELERY_ namespace from Django settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks across all apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Debug task for testing Celery worker.
    Run with: celery -A alx_travel_app worker -l info
    """
    print(f"✅ Debug Task Executed | Request: {self.request!r}")
