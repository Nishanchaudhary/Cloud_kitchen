from django.contrib import admin
from .models import (
    User, Restaurant, MenuCategory, MenuItem,
    Order, OrderItem, Delivery, SupportTicket,
    Review, Payment, Transaction
)

# User Management
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username','profile_picture', 'email', 'role', 'phone_number', 'address')
    list_filter = ('role',)
    search_fields = ('username', 'email', 'phone_number')

# Restaurant & Menu Management
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'email')
    search_fields = ('name', 'phone_number', 'email')

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','image', 'restaurant')
    list_filter = ('restaurant',)
    search_fields = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name','image','description', 'category', 'price', 'is_available')
    list_filter = ('name','price','category', 'is_available')
    search_fields = ('name', 'description')

# Order Management
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant','total_amount', 'status', 'created_at')
    list_filter = ('status', 'restaurant')
    search_fields = ('user__username', 'restaurant__name')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity')
    list_filter = ('order', 'menu_item')
    search_fields = ('order__id', 'menu_item__name')

# Delivery Management
@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_partner', 'status', 'estimated_delivery_time', 'actual_delivery_time')
    list_filter = ('status', 'delivery_partner')
    search_fields = ('order__id', 'delivery_partner__username')

# Customer Support & Notifications
@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'subject')

# Reviews & Ratings
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'order__id')

# Payment and Transactions
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'transaction_id', 'amount', 'status', 'created_at')
    list_filter = ('payment_method', 'status')
    search_fields = ('order__id', 'transaction_id')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('payment', 'created_at')
    search_fields = ('payment__transaction_id',)