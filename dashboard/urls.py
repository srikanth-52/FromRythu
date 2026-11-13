from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.role_redirect_view, name='role_redirect'),
    path('admin-panel/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/farmers/', views.admin_farmers_view, name='admin_farmers'),
    path('admin-panel/farmers/approve/<int:farmer_id>/', views.admin_approve_farmer_view, name='admin_approve_farmer'),
    path('admin-panel/customers/', views.admin_customers_view, name='admin_customers'),
    path('admin-panel/products/', views.admin_products_view, name='admin_products'),
    path('admin-panel/inventory/', views.admin_inventory_view, name='admin_inventory'),
    path('admin-panel/orders/', views.admin_orders_view, name='admin_orders'),
    path('admin-panel/prices/', views.admin_prices_view, name='admin_prices'),
    path('admin-panel/messages/', views.admin_messages_view, name='admin_messages'),
    path('admin-panel/reports/', views.admin_reports_view, name='admin_reports'),
]

