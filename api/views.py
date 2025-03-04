import os
import logging
import requests
from .models import *
from api.models import User 
from .serializers import *
from decouple import config
from django.conf import settings
from rest_framework import status
from rest_framework import viewsets
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from rest_framework.views import APIView
from .serializers import UserSerializer
from reportlab.lib.pagesizes import letter
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, logout


# User management
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete() 
        logout(request)  
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

# Restaurant & Menu Management

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

# Order Management
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

# Delivery Management
class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

# Customer Support & Notifications
class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer

# Reviews & Ratings
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

#payment and transaction

# Set up logging
logger = logging.getLogger(__name__)

class InitiatePaymentView(APIView):
    def post(self, request, order_id):
        try:
            # Validate order_id
            if not order_id:
                return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the order
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

            # Validate payment method
            payment_method = request.data.get('payment_method')
            if payment_method not in ['esewa', 'khalti', 'fonepay']:
                return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

            amount = order.total_amount

            # Initiate payment based on the payment method
            if payment_method == 'esewa':
                return self.initiate_esewa_payment(order, amount)
            elif payment_method == 'khalti':
                return self.initiate_khalti_payment(order, amount)
            elif payment_method == 'fonepay':
                return self.initiate_fonepay_payment(order, amount)

        except Exception as e:
            logger.error(f"Error in InitiatePaymentView: {str(e)}")
            return Response({"error": "An internal error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def initiate_esewa_payment(self, order, amount):
        esewa_url = config('ESEWA_URL')  # Load from .env
        payload = {
            'amount': amount,
            'order_id': order.id,
            'success_url': config('ESEWA_SUCCESS_URL'),
            'failure_url': config('ESEWA_FAILURE_URL'),
        }
        try:
            response = requests.post(esewa_url, data=payload)
            if response.status_code == 200:
                return Response({"payment_url": response.json().get('payment_url')})
            else:
                logger.error(f"Esewa payment initiation failed: {response.status_code} - {response.text}")
                return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error in initiate_esewa_payment: {str(e)}")
            return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def initiate_khalti_payment(self, order, amount):
        khalti_url = config('KHALTI_URL')  # Load from .env
        headers = {
            'Authorization': f'Key {config("KHALTI_SECRET_KEY")}',  # Load from .env
        }
        payload = {
            'amount': int(amount * 100),  # Convert to paisa
            'order_id': order.id,
            'return_url': config('KHALTI_RETURN_URL'),
        }
        try:
            response = requests.post(khalti_url, headers=headers, json=payload)
            if response.status_code == 200:
                return Response({"payment_url": response.json().get('payment_url')})
            else:
                logger.error(f"Khalti payment initiation failed: {response.status_code} - {response.text}")
                return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error in initiate_khalti_payment: {str(e)}")
            return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def initiate_fonepay_payment(self, order, amount):
        fonepay_url = config('FONEPAY_URL')  
        payload = {
            'amount': amount,
            'order_id': order.id,
            'return_url': config('FONEPAY_RETURN_URL'),
        }
        try:
            response = requests.post(fonepay_url, data=payload)
            if response.status_code == 200:
                return Response({"payment_url": response.json().get('payment_url')})
            else:
                logger.error(f"Fonepay payment initiation failed: {response.status_code} - {response.text}")
                return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error in initiate_fonepay_payment: {str(e)}")
            return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentCallbackView(APIView):
    def post(self, request):
        try:
            # Validate input data
            transaction_id = request.data.get('transaction_id')
            payment_method = request.data.get('payment_method')
            order_id = request.data.get('order_id')

            if not transaction_id or not payment_method or not order_id:
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            if payment_method not in ['esewa', 'khalti', 'fonepay']:
                return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

            # Verify payment based on the payment method
            if payment_method == 'esewa':
                return self.verify_esewa_payment(transaction_id, order_id)
            elif payment_method == 'khalti':
                return self.verify_khalti_payment(transaction_id, order_id)
            elif payment_method == 'fonepay':
                return self.verify_fonepay_payment(transaction_id, order_id)

        except Exception as e:
            logger.error(f"Error in PaymentCallbackView: {str(e)}")
            return Response({"error": "An internal error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def verify_esewa_payment(self, transaction_id, order_id):
        esewa_url = f"{config('ESEWA_URL')}/verify/{transaction_id}"  
        try:
            response = requests.get(esewa_url)
            if response.status_code == 200 and response.json().get('status') == 'success':
                self.update_payment_status(order_id, transaction_id, 'completed')
                return Response({"message": "Payment successful"})
            else:
                self.update_payment_status(order_id, transaction_id, 'failed')
                logger.error(f"Esewa payment verification failed: {response.status_code} - {response.text}")
                return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in verify_esewa_payment: {str(e)}")
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

    def verify_khalti_payment(self, transaction_id, order_id):
        khalti_url = f"{config('KHALTI_URL')}/verify/{transaction_id}"  
        headers = {
            'Authorization': f'Key {config("KHALTI_SECRET_KEY")}', 
        }
        try:
            response = requests.get(khalti_url, headers=headers)
            if response.status_code == 200 and response.json().get('status') == 'success':
                self.update_payment_status(order_id, transaction_id, 'completed')
                return Response({"message": "Payment successful"})
            else:
                self.update_payment_status(order_id, transaction_id, 'failed')
                logger.error(f"Khalti payment verification failed: {response.status_code} - {response.text}")
                return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in verify_khalti_payment: {str(e)}")
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

    def verify_fonepay_payment(self, transaction_id, order_id):
        fonepay_url = f"{config('FONEPAY_URL')}/verify/{transaction_id}"  
        try:
            response = requests.get(fonepay_url)
            if response.status_code == 200 and response.json().get('status') == 'success':
                self.update_payment_status(order_id, transaction_id, 'completed')
                return Response({"message": "Payment successful"})
            else:
                self.update_payment_status(order_id, transaction_id, 'failed')
                logger.error(f"Fonepay payment verification failed: {response.status_code} - {response.text}")
                return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in verify_fonepay_payment: {str(e)}")
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

    def update_payment_status(self, order_id, transaction_id, status):
        try:
            order = Order.objects.get(id=order_id)
            payment = Payment.objects.create(
                order=order,
                payment_method='esewa',  # Update this based on the actual payment method
                transaction_id=transaction_id,
                amount=order.total_amount,
                status=status,
            )
            Transaction.objects.create(
                payment=payment,
                transaction_data=response.json(),
            )
        except Exception as e:
            logger.error(f"Error updating payment status: {str(e)}")
            raise ValidationError(f"Failed to update payment status: {str(e)}")




#Invoicing
def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Create PDF
    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, f"Invoice for Order #{order.id}")
    p.drawString(100, 730, f"Amount: {order.total_amount}")
    p.showPage()
    p.save()

    return response