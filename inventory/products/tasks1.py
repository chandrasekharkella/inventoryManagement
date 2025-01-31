# tasks.py
import requests
from celery import shared_task
from celery.exceptions import Retry
from django.utils.timezone import now
import logging
from django.core.mail import send_mail
from inventory.settings import development

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5)
def send_webhook(self, url, payload):
    try:
        logger.info(f"Attempting to send webhook to {url}")
        response = requests.post(url, json=payload, timeout=10)  # Add timeout
        response.raise_for_status()
        logger.info("Webhook sent successfully")
    except requests.exceptions.RequestException as exc:
        logger.error(f"Error sending webhook: {str(exc)}")
        retry_delay = 2 ** self.request.retries
        raise self.retry(countdown=retry_delay, exc=exc)
    
@shared_task(bind=True, max_retries=3)
def send_product_notifications(self, webhook_url,payload):
    """
    Send notifications for product updates through various channels
    """
    try:
        # 1. Send Webhook Notification
        send_webhook_notification(webhook_url, payload)
        
        # # 2. Send Email Notification
        # send_email_notification(payload)
        
    
        logger.info(f"All notifications sent for product {payload['product_id']}")
        
    except Exception as exc:
        logger.error(f"Error sending notifications: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

def send_email_notification(payload):
    """Send email notification about price update"""
    try:
        subject = f"Product Price Update: {payload['product_name']}"
        message = (
            f"Product: {payload['product_name']}\n"
            f"Product ID: {payload['product_id']}\n"
            f"Old Price: ${payload['old_price']}\n"
            f"New Price: ${payload['new_price']}\n"
            f"Updated at: {payload['timestamp']}"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=development.EMAIL_BACKEND,
            recipient_list=[development.ADMIN_EMAIL],
            fail_silently=False,
        )
        logger.info(f"Email notification sent for product {payload['product_id']}")
    except Exception as e:
        logger.error(f"Email notification failed: {str(e)}")
        raise

def send_webhook_notification(webhook_url, payload):
    """Send webhook notification"""
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=5,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        logger.info(f"Webhook sent successfully to cellery {webhook_url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook notification failed: {str(e)}")
        raise