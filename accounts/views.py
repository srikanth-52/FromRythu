
import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .forms import (
    FarmerRegistrationForm,
    CustomerRegistrationForm,
    UserLoginForm,
    UserProfileUpdateForm,
)


logger = logging.getLogger(__name__)

AUTH_BACKEND = "django.contrib.auth.backends.ModelBackend"


# =====================================================
# UNIFIED LOGIN
# =====================================================

def unified_login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard:role_redirect")

    if request.method == "POST":

        form = UserLoginForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()

            login(
                request,
                user,
                backend=AUTH_BACKEND
            )

            messages.success(
                request,
                f"Welcome back, {user.first_name or user.username}!"
            )

            return redirect("dashboard:role_redirect")

    else:
        form = UserLoginForm()

    return render(
        request,
        "accounts/unified_login.html",
        {"form": form}
    )


# =====================================================
# FARMER LOGIN
# =====================================================

def farmer_login_view(request):

    if request.user.is_authenticated:

        if request.user.role == "farmer":
            return redirect("farmers:dashboard")

        return redirect("dashboard:role_redirect")

    if request.method == "POST":

        form = UserLoginForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()

            if user.role != "farmer":

                messages.error(
                    request,
                    "This account is not registered as a Farmer. "
                    "Please use the correct login portal."
                )

            else:

                login(
                    request,
                    user,
                    backend=AUTH_BACKEND
                )

                messages.success(
                    request,
                    f"Welcome to Farmer Portal, "
                    f"{user.first_name or user.username}!"
                )

                return redirect("farmers:dashboard")

    else:
        form = UserLoginForm()

    return render(
        request,
        "accounts/farmer_login.html",
        {"form": form}
    )


# =====================================================
# CUSTOMER LOGIN
# =====================================================

def customer_login_view(request):

    if request.user.is_authenticated:

        if request.user.role == "customer":
            return redirect("customers:dashboard")

        return redirect("dashboard:role_redirect")

    if request.method == "POST":

        form = UserLoginForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()

            if user.role != "customer":

                messages.error(
                    request,
                    "This account is not registered as a Customer. "
                    "Please use the correct login portal."
                )

            else:

                login(
                    request,
                    user,
                    backend=AUTH_BACKEND
                )

                messages.success(
                    request,
                    f"Welcome to FromRythu, "
                    f"{user.first_name or user.username}!"
                )

                return redirect("customers:dashboard")

    else:
        form = UserLoginForm()

    return render(
        request,
        "accounts/customer_login.html",
        {"form": form}
    )


# =====================================================
# ADMIN LOGIN
# =====================================================

def admin_login_view(request):

    if request.user.is_authenticated:

        if (
            request.user.is_superuser
            or request.user.is_staff
            or request.user.role == "admin"
        ):
            return redirect("dashboard:admin_dashboard")

    if request.method == "POST":

        form = UserLoginForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()

            if not (
                user.is_superuser
                or user.is_staff
                or user.role == "admin"
            ):

                messages.error(
                    request,
                    "Unauthorized access. Admin privileges required."
                )

            else:

                login(
                    request,
                    user,
                    backend=AUTH_BACKEND
                )

                messages.success(
                    request,
                    "Admin Portal Authenticated."
                )

                return redirect("dashboard:admin_dashboard")

    else:
        form = UserLoginForm()

    return render(
        request,
        "accounts/admin_login.html",
        {"form": form}
    )


# =====================================================
# REGISTRATION SELECTION
# =====================================================

def register_selection_view(request):

    return render(
        request,
        "accounts/register.html"
    )


# =====================================================
# FARMER REGISTRATION
# =====================================================

def register_farmer_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard:role_redirect")

    if request.method == "POST":

        form = FarmerRegistrationForm(request.POST)

        if form.is_valid():

            try:

                with transaction.atomic():

                    user = form.save()

                login(
                    request,
                    user,
                    backend=AUTH_BACKEND
                )

                messages.success(
                    request,
                    "Farmer account created successfully! "
                    "Welcome to FromRythu."
                )

                return redirect("farmers:dashboard")

            except Exception:

                logger.exception(
                    "Farmer registration failed."
                )

                messages.error(
                    request,
                    "Unable to create your farmer account. "
                    "Please check the server logs."
                )

        else:

            logger.warning(
                "Farmer registration validation failed: %s",
                form.errors.as_json()
            )

            messages.error(
                request,
                "Please correct the errors in the registration form."
            )

    else:
        form = FarmerRegistrationForm()

    return render(
        request,
        "accounts/register_farmer.html",
        {"form": form}
    )


# =====================================================
# CUSTOMER REGISTRATION
# =====================================================

def register_customer_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard:role_redirect")

    if request.method == "POST":

        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():

            try:

                with transaction.atomic():

                    user = form.save()

                login(
                    request,
                    user,
                    backend=AUTH_BACKEND
                )

                messages.success(
                    request,
                    "Customer account created successfully! "
                    "Welcome to FromRythu."
                )

                return redirect("customers:dashboard")

            except Exception:

                logger.exception(
                    "Customer registration failed."
                )

                messages.error(
                    request,
                    "Unable to create your customer account. "
                    "Please check the server logs."
                )

        else:

            logger.warning(
                "Customer registration validation failed: %s",
                form.errors.as_json()
            )

            messages.error(
                request,
                "Please correct the errors in the registration form."
            )

    else:
        form = CustomerRegistrationForm()

    return render(
        request,
        "accounts/register_customer.html",
        {"form": form}
    )


# =====================================================
# USER PROFILE
# =====================================================

@login_required
def profile_view(request):

    user = request.user

    if request.method == "POST":

        form = UserProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=user
        )

        if form.is_valid():

            try:

                form.save()

                messages.success(
                    request,
                    "Your profile has been updated successfully."
                )

                return redirect("accounts:profile")

            except Exception:

                logger.exception(
                    "Profile update failed."
                )

                messages.error(
                    request,
                    "Unable to update your profile. Please try again."
                )

    else:

        form = UserProfileUpdateForm(instance=user)

    farmer_profile = getattr(
        user,
        "farmer_profile",
        None
    )

    customer_profile = getattr(
        user,
        "customer_profile",
        None
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "farmer_profile": farmer_profile,
            "customer_profile": customer_profile,
        }
    )


# =====================================================
# LOGOUT
# =====================================================

def logout_view(request):

    logout(request)

    messages.info(
        request,
        "You have been logged out successfully."
    )

    return redirect("home")
