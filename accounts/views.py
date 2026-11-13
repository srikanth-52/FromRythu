from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FarmerRegistrationForm, CustomerRegistrationForm, UserLoginForm, UserProfileUpdateForm
from .models import User

def unified_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:role_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard:role_redirect')
        else:
            messages.error(request, "Invalid username or password. Please check your credentials.")
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/unified_login.html', {'form': form})


def farmer_login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'farmer':
            return redirect('farmers:dashboard')
        elif request.user.is_superuser or request.user.role == 'admin':
            return redirect('dashboard:admin_dashboard')
        else:
            return redirect('customers:dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role != 'farmer' and not user.is_superuser:
                messages.warning(request, "This account is registered as a Customer. Redirected to Customer Portal.")
                login(request, user)
                return redirect('customers:dashboard')
            login(request, user)
            messages.success(request, f"Welcome to Rythu Farmer Portal, {user.first_name or user.username}!")
            return redirect('farmers:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/farmer_login.html', {'form': form})


def customer_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:role_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role == 'farmer':
                messages.info(request, "Farmer account detected. Redirecting to Farmer Dashboard.")
                login(request, user)
                return redirect('farmers:dashboard')
            login(request, user)
            messages.success(request, f"Welcome to FromRythu, {user.first_name or user.username}!")
            return redirect('customers:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/customer_login.html', {'form': form})


def admin_login_view(request):
    if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('dashboard:admin_dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not (user.role == 'admin' or user.is_superuser or user.is_staff):
                messages.error(request, "Unauthorized access. Admin privileges required.")
                return redirect('accounts:admin_login')
            login(request, user)
            messages.success(request, "Admin Portal Authenticated.")
            return redirect('dashboard:admin_dashboard')
        else:
            messages.error(request, "Invalid administrator credentials.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/admin_login.html', {'form': form})


def register_selection_view(request):
    return render(request, 'accounts/register.html')


def register_farmer_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:role_redirect')

    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                "Registration submitted successfully! Welcome to FromRythu Farmer Portal. You can now list your harvest."
            )
            return redirect('farmers:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FarmerRegistrationForm()

    return render(request, 'accounts/register_farmer.html', {'form': form})


def register_customer_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:role_redirect')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                "Account created successfully! Welcome to FromRythu. Enjoy pure, fresh produce directly from farmers."
            )
            return redirect('products:list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register_customer.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=user)

    farmer_profile = getattr(user, 'farmer_profile', None)
    customer_profile = getattr(user, 'customer_profile', None)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'farmer_profile': farmer_profile,
        'customer_profile': customer_profile,
    })


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')
