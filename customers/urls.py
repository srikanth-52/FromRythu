from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('messages/', views.messages_view, name='messages'),
]

