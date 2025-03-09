from .views import *
from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'restaurant', RestaurantViewSet)
router.register(r'menucategory', MenuCategoryViewSet)
router.register(r'menuitem', MenuItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'delivery', DeliveryViewSet)
router.register(r'supportticket', SupportTicketViewSet)
router.register(r'review', ReviewViewSet)

custom_urlpatterns = [
    path('orders/<int:order_id>/items/', OrderItemCreateView.as_view(), name='order-item-create'),
    path('orders/<int:order_id>/items/<int:item_id>/', OrderItemUpdateView.as_view(), name='order-item-update'),
    path('orders/<int:order_id>/items/<int:item_id>/delete/', OrderItemDeleteView.as_view(), name='order-item-delete'),
]


urlpatterns = [
    path('kitchen', include(router.urls)),
    path('orders', include(custom_urlpatterns)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('payment/initiate/<int:order_id>/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment-callback'),
    path('invoice/<int:order_id>/', DownloadInvoiceView.as_view(), name='download-invoice'),
]