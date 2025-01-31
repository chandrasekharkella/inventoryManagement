from inventory.celery import app
import requests
from celery.exceptions import MaxRetriesExceededError
import logging
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(requests.RequestException,), retry_backoff=True, retry_backoff_max=60, retry_jitter=True, max_retries=5)
def process_webhook(self, url, payload):
    
    try:
        logger.info(f"Webhook Task Started: {url} | {payload}")
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except requests.RequestException as exc:
        retry_delay = min(2 ** self.request.retries, 60)  # Exponential backoff, max 60 sec
        try:
            self.retry(exc=exc, countdown=retry_delay)
        except MaxRetriesExceededError:
            return {"status": "failed", "error": str(exc)}





