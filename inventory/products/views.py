from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product,User,AuthUsers
from .serializers import ProductSerializer, ProductRequestSerializer, UserSerializer
from datetime import timedelta
from django.utils.timezone import now
import requests
import time
from rest_framework.pagination import PageNumberPagination
import random
from faker import Faker

from rest_framework.permissions import IsAuthenticated
import logging

from inventory.settings import development,test
fake = Faker()
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .tests import mask_email  # Import the mask_email function
from .tasks1 import send_webhook,send_product_notifications,send_webhook_notification # Import the Celery task
from django.core.mail import send_mail
from .tasks import process_webhook
import os

# Set up logging
logger = logging.getLogger(__name__)


# Function to generate dummy products data
class GenerateDummyProductsView(APIView):
    def post(self, request):
        dummy_data = [
            Product(
                name=fake.word(),
                price=round(random.uniform(10, 500), 2),
                available=random.choice([True, False])
            )
            for _ in range(50)
        ]
        Product.objects.bulk_create(dummy_data)
        return Response({'message': '50 dummy products inserted successfully!'}, status=status.HTTP_201_CREATED)

# Custom Pagination Class
class DynamicPageNumberPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'limit'  # Query parameter for dynamic limit
    max_page_size = 100  # Maximum allowed page size

    def get_paginated_response(self, data):
        return Response({
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'total_records': self.page.paginator.count,
            'search_records': len(data),
            'results': data
        })

# Function for product Search api 
class ProductSearchView(APIView):
    # Limit: 100 requests per minute (per user)
    @method_decorator(ratelimit(key='ip', rate='2/m', method='POST', block=False))
    def post(self, request):
        if getattr(request, 'limited', False):  # Check if request was throttled
            return Response(
                {"detail": "Too many requests from this IP. Please try again in a few minutes."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        queryset = Product.objects.all()
        name = request.data.get('name')
        min_price = request.data.get('min_price')
        max_price = request.data.get('max_price')
        available = request.data.get('available')
        active_last_30_days = request.data.get('active_last_30_days')
        page = request.data.get('page')
        limit = request.data.get('limit')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if available is not None:
            available_value = available.lower() == 'true'
            queryset = queryset.filter(available=available_value)
        if active_last_30_days and active_last_30_days.lower() == 'true':
            threshold_date = now() - timedelta(days=30)
            queryset = queryset.filter(updated_at__gte=threshold_date, available=True)

        # Dynamic Pagination
        paginator = DynamicPageNumberPagination()
        paginator.page_size = int(request.query_params.get("limit", paginator.page_size))  # Override default limit
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize and return response
        serializer = ProductSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

# Function Fetch last 30 day active updated products
class ActiveProductsView(APIView):
    def get(self, request):
        last_30_days = now() - timedelta(days=30)
        queryset = Product.objects.filter(updated_at__gte=last_30_days, available=True).order_by('-updated_at')  # Sorting by updated_at DESC

        if not queryset.exists():
            return Response({"message": "No active products in the last 30 days"}, status=status.HTTP_200_OK)

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDataView(APIView):
    # permission_classes = [IsAuthenticated]
    pagination_class = DynamicPageNumberPagination
    def get(self, request):
        try:
           
          
            
            # Get users and apply pagination
            users = AuthUsers.objects.all()
            paginator = self.pagination_class()
            paginator.page_size = int(request.query_params.get("limit", paginator.page_size))
            paginated_users = paginator.paginate_queryset(users, request)
            
            serializer = UserSerializer(paginated_users, many=True)
            
             # Log successful response
            # logger.info(
            #     f"API Response - Status: 200, "
            #     f"Path: {request.path}, "
            #     f"Data: {mask_sensitive_data(response.data)}"
            # )
             # Log the response (with masked emails)
            userEmail ="chandrasekharkella16@gmail.com"
            logger.info(
                f"Retrieved {len(paginated_users)} user records - Request by: {mask_email(userEmail)}"
            )
            
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
             
            print("errorr======",e)
             # Log the error (with masked email)
            logger.error(
                f"Error retrieving user data - Requested by: {mask_email(userEmail)} - Error: {str(e)}"
            )
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving user data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductUpdateView1(APIView):
    def post(self, request):
        # Get the full URL of the current request
        current_url = request.build_absolute_uri()
        # Or if you want just the path without domain
        path_url = request.get_full_path()

        product_id = request.data.get('product_id')
        price = request.data.get('price')

        try:
            product = Product.objects.get(id=product_id)
            product.price = price
            product.save()

            # Use the current URL instead of hardcoded webhook URL
            webhook_url = current_url  # or path_url if you prefer
            print("cureent url",webhook_url)
            payload = {
                'product_id': product_id,
                'price': price,
                'timestamp': now().isoformat()
            }
            send_webhook.delay(webhook_url, payload)

            return Response({'message': 'Product updated successfully!'}, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return Response({'error': 'An error occurred while updating the product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# webhook_receiver/views.py


class WebhookReceiver(APIView):
    def post(self, request):
        try:
            # Log the received data
            logger.info(f"Webhook received from celerey...: {request.data}")
            
            # Extract the data
            product_id = request.data.get('product_id')
            price = request.data.get('price')
            # timestamp = request.data.get('timestamp')
            
            # Validate the data
            if not all([product_id, price]):
                return Response(
                    {'error': 'Missing required fields'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process the webhook and send notifications
            # self.process_product_update(product_id, price)
            
            return Response({'status': 'webhook received and processed'}, 
                          status=status.HTTP_200_OK)
                          
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return Response(
                {'error': 'Error processing webhook'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def process_product_update(self, product_id, price):
        """Process the product update and send notifications"""
        try:
            # 1. Email Notification
            self.send_email_notification(product_id, price)
        except Exception as e:
            logger.error(f"Error in process_product_update: {str(e)}")
            raise

    def send_email_notification(self, product_id, price):
        """Send email notification about price update"""
        subject = f'Product {product_id} Price Updated'
        message = f'The price for product {product_id} has been updated to ${price}'
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=development.EMAIL_BACKEND,
                recipient_list=[development.ADMIN_EMAIL],
                fail_silently=False,
            )
            logger.info(f"Email notification sent for product {product_id}")
        except Exception as e:
            logger.error(f"Email notification failed: {str(e)}")
    

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
            # webhook_url = development.WEBHOOK_URL
            if os.environ.get('DJANGO_SETTINGS_MODULE') == 'inventory.settings.development':
                webhook_url = development.WEBHOOK_URL
                

            if os.environ.get('DJANGO_SETTINGS_MODULE') == 'inventory.settings.test':
                webhook_url = test.WEBHOOK_URL
                

            # Prepare webhook payload
            timestamp = now()
            payload = {
                'product_id': product_id,
                'old_price': str(old_price),
                'price': str(price),
                'product_name': product.name,
                'timestamp': timestamp.isoformat()
            }

            # Send notifications via Celery task with webhook URL
            
           
            process_webhook.delay(webhook_url, payload)
            self.process(webhook_url, payload)
            

            return Response({
                'message': 'Product updated successfully!',
                'data': payload
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return Response(
                {'error': {str(e)}}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def process(self, webhook_url, payload):
        
        try:
            logger.info(f"Webhook Task Started: {webhook_url} | {payload}")
            response = requests.post(webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            return {"status": "success", "response": response.json()}
           
        except Exception as e:
            logger.error(f"Email notification failed: {str(e)}")
        
