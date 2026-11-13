from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('api/product/<int:product_id>/history/', views.stock_history_api, name='product_history_api'),
]

