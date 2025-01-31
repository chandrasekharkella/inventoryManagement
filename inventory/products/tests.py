
import logging
import requests
from celery.exceptions import MaxRetriesExceededError
logger = logging.getLogger(__name__)

# products/utils.py
def mask_email(email):
    """
    Masks email addresses with custom pattern:
    Username: First 3 letters and last 2 letters visible, rest masked
    Domain: First 2 letters and last letter visible, rest masked
    Example: johndoe@example.com -> joh***oe@ex****e.com
    """
    if not email or '@' not in email:
        return email
        
    username, domain = email.split('@')
    domain_parts = domain.split('.')
    
    # Mask username - show first 3 and last 2 letters
    if len(username) <= 5:  # Handle short usernames
        masked_username = username  # Keep very short usernames as is
    else:
        visible_start = username[:3]
        visible_end = username[-2:]
        mask_length = len(username) - 5  # Length minus (first 3 + last 2)
        masked_username = visible_start + '*' * mask_length + visible_end
    
    # Mask domain - show first 2 and last letter
    domain_name = domain_parts[0]
    if len(domain_name) <= 3:  # Handle short domains
        masked_domain = domain_name  # Keep very short domains as is
    else:
        visible_start = domain_name[:2]
        visible_end = domain_name[-1]
        mask_length = len(domain_name) - 3  # Length minus (first 2 + last 1)
        masked_domain = visible_start + '*' * mask_length + visible_end
    
    return f"{masked_username}@{masked_domain}.{domain_parts[-1]}"

def process(self,url, payload):
    
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
