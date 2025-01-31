# tasks.py
from celery import shared_task
import pika
import json
import logging
from django.conf import settings
import requests
from django.core.mail import send_mail
from inventory.settings import development

logger = logging.getLogger(__name__)

class RabbitMQPublisher:
    def __init__(self):
        self.credentials = pika.PlainCredentials('guest', 'guest')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672,
                credentials=self.credentials
            )
        )
        self.channel = self.connection.channel()
        
        # Declare exchanges
        self.channel.exchange_declare(
            exchange='product_updates',
            exchange_type='topic',
            durable=True
        )
        
        # Declare queues
        self.channel.queue_declare(queue='email_notifications', durable=True)
        self.channel.queue_declare(queue='slack_notifications', durable=True)
        self.channel.queue_declare(queue='webhook_notifications', durable=True)
        
        # Bind queues to exchange
        self.channel.queue_bind(
            exchange='product_updates',
            queue='email_notifications',
            routing_key='product.update.email'
        )
        self.channel.queue_bind(
            exchange='product_updates',
            queue='slack_notifications',
            routing_key='product.update.slack'
        )
        self.channel.queue_bind(
            exchange='product_updates',
            queue='webhook_notifications',
            routing_key='product.update.webhook'
        )

    def publish_message(self, routing_key, message):
        self.channel.basic_publish(
            exchange='product_updates',
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )

    def close(self):
        self.connection.close()

@shared_task(bind=True, max_retries=3)
def process_product_update(self, webhook_url, payload):
    """
    Process product update and publish messages to RabbitMQ
    """
    try:
        publisher = RabbitMQPublisher()
        
        # Publish to different queues based on notification type
        publisher.publish_message('product.update.webhook', {
            'webhook_url': webhook_url,
            'payload': payload
        })
        
        publisher.publish_message('product.update.email', payload)
        publisher.publish_message('product.update.slack', payload)
        
        publisher.close()
        logger.info(f"Messages published for product {payload['product_id']}")
        
    except Exception as exc:
        logger.error(f"Error publishing messages: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

# Consumer tasks
@shared_task
def process_webhook_notification(body):
    data = json.loads(body)
    webhook_url = data['webhook_url']
    payload = data['payload']
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=5,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        logger.info(f"Webhook sent successfully to {webhook_url}")
    except Exception as e:
        logger.error(f"Webhook notification failed: {str(e)}")
        raise

@shared_task
def process_email_notification(body):
    data = json.loads(body)
    try:
        subject = f"Product Price Update: {data['product_name']}"
        message = (
            f"Product: {data['product_name']}\n"
            f"Product ID: {data['product_id']}\n"
            f"Old Price: ${data['old_price']}\n"
            f"New Price: ${data['new_price']}\n"
            f"Updated at: {data['timestamp']}"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        logger.info(f"Email notification sent for product {data['product_id']}")
    except Exception as e:
        logger.error(f"Email notification failed: {str(e)}")
        raise

@shared_task
def process_slack_notification(body):
    data = json.loads(body)
    try:
        message = {
            "text": (
                f"🔔 Product Price Update Alert!\n"
                f"Product: {data['product_name']}\n"
                f"Product ID: {data['product_id']}\n"
                f"Old Price: ${data['old_price']}\n"
                f"New Price: ${data['new_price']}\n"
                f"Updated at: {data['timestamp']}"
            )
        }
        response = requests.post(
            settings.SLACK_WEBHOOK_URL,
            json=message,
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"Slack notification sent for product {data['product_id']}")
    except Exception as e:
        logger.error(f"Slack notification failed: {str(e)}")
        raise

# views.py
class ProductUpdateView(APIView):
    def post(self, request):
        try:
            # Extract data from request
            product_id = request.data.get('product_id')
            price = request.data.get('price')
            
            if not all([product_id, price]):
                return Response(
                    {'error': 'Missing required fields'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update product
            try:
                product = Product.objects.get(id=product_id)
                old_price = product.price
                product.price = price
                product.save()
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get webhook URL from settings
            webhook_url = settings.WEBHOOK_URL

            # Prepare webhook payload
            timestamp = now()
            payload = {
                'product_id': product_id,
                'old_price': str(old_price),
                'new_price': str(price),
                'product_name': product.name,
                'timestamp': timestamp.isoformat()
            }

            # Send to RabbitMQ via Celery task
            process_product_update.delay(webhook_url, payload)

            return Response({
                'message': 'Product updated successfully!',
                'data': payload
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return Response(
                {'error': 'An error occurred while updating the product'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )