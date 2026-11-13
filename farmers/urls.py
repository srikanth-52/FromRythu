from django.urls import path
from . import views

app_name = 'farmers'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add-product/', views.add_product_view, name='add_product'),
    path('manage-products/', views.manage_products_view, name='manage_products'),
    path('edit-product/<int:pk>/', views.edit_product_view, name='edit_product'),
    path('toggle-product/<int:pk>/', views.toggle_product_active_view, name='toggle_product'),
    path('stock/', views.stock_view, name='stock'),
    path('price/', views.price_view, name='price'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/update/<int:item_id>/', views.update_item_status_view, name='update_order_status'),
    path('messages/', views.messages_view, name='messages'),
    path('sales-report/', views.sales_report_view, name='sales_report'),
]

