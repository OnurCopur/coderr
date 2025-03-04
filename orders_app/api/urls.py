from django.urls import path
from .views import OrderListCreateView, OrderDetailView, OrderCountView, CompletedOrderCountView

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('orders/completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
]
