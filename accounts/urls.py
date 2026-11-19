
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Login
    path("login/", views.unified_login_view, name="login"),
    path("farmer-login/", views.farmer_login_view, name="farmer_login"),
    path("customer-login/", views.customer_login_view, name="customer_login"),
    path("admin-login/", views.admin_login_view, name="admin_login"),

    # Registration
    path("register/", views.register_selection_view, name="register"),
    path("register/farmer/", views.register_farmer_view, name="register_farmer"),
    path("register/customer/", views.register_customer_view, name="register_customer"),

    # Profile
    path("profile/", views.profile_view, name="profile"),

    # Logout
    path("logout/", views.logout_view, name="logout"),
]
