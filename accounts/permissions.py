from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def farmer_required(view_func):
    """
    Decorator for views that checks if the logged-in user is a Farmer.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to your Farmer account to access this page.")
            return redirect('accounts:farmer_login')
        if not (request.user.role == 'farmer' or request.user.is_superuser):
            messages.error(request, "Access restricted: Farmer credentials required.")
            return redirect('dashboard:role_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def customer_required(view_func):
    """
    Decorator for views that checks if the logged-in user is a Customer.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to your Customer account to continue.")
            return redirect('accounts:customer_login')
        if not (request.user.role == 'customer' or request.user.is_superuser):
            messages.error(request, "Access restricted: Customer account required.")
            return redirect('dashboard:role_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """
    Decorator for views that checks if the logged-in user is an Admin or Staff.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in with Admin privileges.")
            return redirect('accounts:admin_login')
        if not (request.user.role == 'admin' or request.user.is_superuser or request.user.is_staff):
            messages.error(request, "Access restricted: Admin Portal authorization required.")
            return redirect('dashboard:role_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

