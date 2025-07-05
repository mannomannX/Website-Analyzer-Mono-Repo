# app/worker/celery_app.py

from celery import Celery
from app.core.config import settings

redis_url = f"redis://{settings.REDIS_HOST}:6379/0"

celery_app = Celery(
    "worker",
    broker=redis_url,
    backend=redis_url
)

# Sagt Celery nur noch, wo es nach Tasks suchen soll.
celery_app.autodiscover_tasks(["app.worker"])