from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('order/<str:order_number>/', views.payment_detail_view, name='detail'),
]

