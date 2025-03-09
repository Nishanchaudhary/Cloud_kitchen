from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# User management
class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name="api_users",  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="api_user_permissions",  
        blank=True
    )
    USER_ROLES = (
        ('admin', 'Admin'),
        ('kitchen_staff', 'Kitchen Staff'),
        ('delivery_partner', 'Delivery Partner'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
   

    def __str__(self):
        return self.username

# Restaurant & Menu Management
class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name

class MenuCategory(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='menuitem_images/', null=True, blank=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Order Management
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

# Delivery_Management
class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deliveries')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, default='pending')
    estimated_delivery_time = models.DateTimeField()
    actual_delivery_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery for Order {self.order.id}"

# Customer Support & Notifications
class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

# Reviews & Ratings
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for Order {self.order.id}"

# Payment and Transactions


class Payment(models.Model):
    PAYMENT_METHODS = (
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
        ('fonepay', 'Fonepay'),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.id}"

class Transaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_data = models.JSONField()  # Store raw response from payment gateway
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction for Payment {self.payment.transaction_id}"

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE,  unique=True, related_name='invoice')
    invoice_file = models.FileField(upload_to='invoices/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for Order #{self.order.id}"