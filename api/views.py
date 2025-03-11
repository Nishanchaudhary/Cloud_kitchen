from django.utils.http import urlsafe_base64_encode  
from django.utils.encoding import force_bytes 
import os
import logging
import requests
from .models import *
from .serializers import *
from io import BytesIO 
from decouple import config
from api.models import User
from django.conf import settings
from rest_framework import status
from rest_framework import viewsets
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.core.mail import send_mail
from rest_framework.views import APIView
from .serializers import UserSerializer
from reportlab.lib.pagesizes import letter
from django.utils.encoding import force_str
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, logout
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle



# Set up logging
logger = logging.getLogger(__name__)

# User Management
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class RegisterView(APIView):
    @method_decorator(csrf_protect)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    throttle_classes = [AnonRateThrottle]

    @method_decorator(csrf_protect)
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
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    @method_decorator(csrf_protect)
    def post(self, request):
        email = request.data.get('email')
        frontend_url = request.data.get('frontend_url')  

        if not frontend_url:
            return Response(
                {'error': 'Frontend URL is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,  
                [user.email],  
                fail_silently=False,
            )

            return Response(
                {'message': 'Password reset link sent to your email'}, 
                status=status.HTTP_200_OK
            )
        return Response(
            {'error': 'User with this email does not exist'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
from django.utils.http import urlsafe_base64_decode
class ResetPasswordView(APIView):
    @method_decorator(csrf_protect)
    def post(self, request, uidb64, token):
        try:
            # Decode the uidb64 and get the user
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            # Check if the token is valid for the user
            if default_token_generator.check_token(user, token):
                new_password = request.data.get('new_password')
                
                # Set the new password and save the user
                user.set_password(new_password)
                user.save()
                
                return Response(
                    {'message': 'Password reset successfully'}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Invalid token'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid user'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# Restaurant & Menu Management
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [IsAuthenticated]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

# Order Management
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class OrderItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)
            order.total_amount = sum(item.menu_item.price * item.quantity for item in order.items.all())
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, order_id, item_id):
        order_item = get_object_or_404(OrderItem, id=item_id, order_id=order_id)
        serializer = OrderItemSerializer(order_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            order = order_item.order
            order.total_amount = sum(item.menu_item.price * item.quantity for item in order.items.all())
            order.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, order_id, item_id):
        order_item = get_object_or_404(OrderItem, id=item_id, order_id=order_id)
        order = order_item.order
        order_item.delete()
        order.total_amount = sum(item.menu_item.price * item.quantity for item in order.items.all())
        order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Delivery Management
class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

# Customer Support & Notifications
class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

# Reviews & Ratings
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

# Payment and Transaction
class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @method_decorator(csrf_protect)
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
        esewa_url = config('ESEWA_URL')  
        payload = {
            'amount': amount,
            'order_id': order.id,
            'success_url': config('ESEWA_SUCCESS_URL'),
            'failure_url': config('ESEWA_FAILURE_URL'),
        }
        try:
            response = requests.post(esewa_url, data=payload, verify=True)  
            if response.status_code == 200:
                return Response({"payment_url": response.json().get('payment_url')})
            else:
                logger.error(f"Esewa payment initiation failed: {response.status_code} - {response.text}")
                return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error in initiate_esewa_payment: {str(e)}")
            return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def initiate_khalti_payment(self, order, amount):
        khalti_url = config('KHALTI_URL')  
        headers = {
            'Authorization': f'Key {config("KHALTI_SECRET_KEY")}',  
        }
        payload = {
            'amount': int(amount * 100),  # Convert to paisa
            'order_id': order.id,
            'return_url': config('KHALTI_RETURN_URL'),
        }
        try:
            response = requests.post(khalti_url, headers=headers, json=payload, verify=True)  # Ensure HTTPS
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
            response = requests.post(fonepay_url, data=payload, verify=True) 
            if response.status_code == 200:
                return Response({"payment_url": response.json().get('payment_url')})
            else:
                logger.error(f"Fonepay payment initiation failed: {response.status_code} - {response.text}")
                return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error in initiate_fonepay_payment: {str(e)}")
            return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentCallbackView(APIView):
    @method_decorator(csrf_protect)
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
            response = requests.get(esewa_url, verify=True) 
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
            response = requests.get(khalti_url, headers=headers, verify=True)  
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
            response = requests.get(fonepay_url, verify=True) 
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

# Invoicing
class DownloadInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            
            order = Order.objects.get(id=order_id)
            if order.user != request.user: 
                return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

            # Create a PDF response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

            # Create a PDF document in memory
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(100, 750, "Cloud Kitchen")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(100, 730, "Thank you for choosing us! We hope you enjoy your meal.")
            pdf.drawString(100, 710, f"Invoice ID: #{order.id}")
            pdf.drawString(100, 690, f"Customer Name: {order.user.username}")
            pdf.drawString(100, 670, f"Restaurant: {order.restaurant.name}")
            pdf.drawString(100, 650, f"Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            pdf.drawString(100, 630, f"Order Status: {order.get_status_display()}")
            pdf.drawString(100, 610, f"Total Amount: {order.total_amount}")
            pdf.drawString(100, 590, "Order Items:")
            y = 570
            for item in order.items.all():  # Access order items using the related_name 'items'
                pdf.drawString(120, y, f"{item.menu_item.name} - {item.quantity} x {item.menu_item.price}")
                y -= 20

            # Save the PDF
            pdf.showPage()
            pdf.save()
            pdf_content = buffer.getvalue()
            buffer.close()
            file_name = f"invoice_{order.id}.pdf"
            file_path = os.path.join(settings.MEDIA_ROOT, "invoices", file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(pdf_content)

            # Store the file path in the database
            invoice = Invoice.objects.create(
                order=order,
                invoice_file=file_path,
            )
            invoice.save()

            # Return the PDF as a downloadable response
            response.write(pdf_content)
            return response

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generating invoice: {str(e)}")
            return Response({"error": "An internal error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)