
import logging

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from .models import User, EmailOTP
from .forms import (
    FarmerRegistrationForm,
    CustomerRegistrationForm,
    UserLoginForm,
    UserProfileUpdateForm,
)


logger = logging.getLogger(__name__)

AUTH_BACKEND = "django.contrib.auth.backends.ModelBackend"


def mask_email(email):
    if not email or "@" not in email:
        return email
    user_part, domain_part = email.split("@", 1)
    if len(user_part) <= 2:
        masked_user = user_part[0] + "*"
    else:
        masked_user = user_part[0] + "*" * (len(user_part) - 2) + user_part[-1]
    return f"{masked_user}@{domain_part}"


# =====================================================
# EMAIL OTP SEND & VERIFY
# =====================================================

def send_otp_view(request):
    if request.method != "POST":
        return redirect("accounts:login")

    portal = request.POST.get("portal", "unified")
    email_or_user = request.POST.get("email_or_username", "").strip()

    if portal == "farmer":
        redirect_url = reverse("accounts:farmer_login") + "?tab=otp"
    elif portal == "customer":
        redirect_url = reverse("accounts:customer_login") + "?tab=otp"
    else:
        redirect_url = reverse("accounts:login") + "?tab=otp"

    if not email_or_user:
        messages.error(request, "Please enter your registered email address or username.")
        return redirect(redirect_url)

    if "@" in email_or_user:
        user = User.objects.filter(email__iexact=email_or_user).first()
    else:
        user = User.objects.filter(username__iexact=email_or_user).first()
        if not user:
            user = User.objects.filter(email__iexact=email_or_user).first()

    if not user:
        messages.error(request, "No account found matching this email or username.")
        return redirect(redirect_url)

    if not user.email:
        messages.error(
            request,
            "This account has no registered email. Please use password login or update your profile."
        )
        return redirect(redirect_url)

    # Validate portal role
    if portal == "farmer":
        if not (user.role == "farmer" or user.is_admin_role or user.role == "admin"):
            messages.error(request, "This account is not registered as a Farmer.")
            return redirect(redirect_url)
    elif portal == "customer":
        if user.role != "customer":
            messages.error(request, "This account is not registered as a Customer.")
            return redirect(redirect_url)

    otp_record = EmailOTP.generate_otp(email=user.email, user=user)

    request.session["otp_user_id"] = user.id
    request.session["otp_email"] = user.email
    request.session["otp_portal"] = portal
    request.session["otp_masked_email"] = mask_email(user.email)
    request.session["otp_sent"] = True

    subject = f"{otp_record.otp} is your FromRythu Login OTP"
    email_body = (
        f"Hello {user.first_name or user.username},\n\n"
        f"Your One-Time Password (OTP) to log in to FromRythu is:\n\n"
        f"    {otp_record.otp}\n\n"
        f"This code is valid for 10 minutes.\n"
        f"If you did not request this OTP, you can safely ignore this email.\n\n"
        f"Best regards,\n"
        f"FromRythu Team - Direct Farm to Customer Marketplace"
    )

    try:
        send_mail(
            subject=subject,
            message=email_body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "FromRythu <noreply@fromrythu.com>"),
            recipient_list=[user.email],
            fail_silently=False,
        )
        messages.success(request, f"A 6-digit OTP has been sent to {mask_email(user.email)}. Please check your inbox.")
    except Exception as e:
        logger.warning(f"send_mail failed: {e}")
        messages.success(
            request,
            f"OTP sent to {mask_email(user.email)}! (Demo/Dev code: {otp_record.otp})"
        )

    return redirect(redirect_url)


def verify_otp_view(request):
    if request.method != "POST":
        return redirect("accounts:login")

    portal = request.POST.get("portal", "unified")
    entered_otp = request.POST.get("otp", "").strip()

    if portal == "farmer":
        redirect_url = reverse("accounts:farmer_login") + "?tab=otp"
    elif portal == "customer":
        redirect_url = reverse("accounts:customer_login") + "?tab=otp"
    else:
        redirect_url = reverse("accounts:login") + "?tab=otp"

    user_id = request.session.get("otp_user_id")
    email = request.session.get("otp_email")

    if not user_id or not email:
        messages.error(request, "OTP session expired. Please request a new OTP.")
        return redirect(redirect_url)

    otp_record = EmailOTP.objects.filter(
        email__iexact=email,
        otp=entered_otp,
        is_used=False
    ).first()

    if not otp_record or not otp_record.is_valid():
        messages.error(request, "Invalid or expired OTP. Please enter the correct 6-digit code or request a new one.")
        return redirect(redirect_url)

    otp_record.is_used = True
    otp_record.save()

    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "Account error. Please try again.")
        return redirect(redirect_url)

    login(request, user, backend=AUTH_BACKEND)

    for k in ["otp_user_id", "otp_email", "otp_portal", "otp_masked_email", "otp_sent"]:
        request.session.pop(k, None)

    messages.success(request, f"Welcome back, {user.first_name or user.username}!")

    if portal == "farmer":
        if user.is_admin_role or user.role == "admin":
            return redirect("dashboard:admin_dashboard")
        return redirect("farmers:dashboard")
    elif portal == "customer":
        return redirect("customers:dashboard")
    else:
        return redirect("dashboard:role_redirect")


# =====================================================
# UNIFIED LOGIN
# =====================================================

def unified_login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard:role_redirect")

    if request.GET.get("cancel_otp"):
        for k in ["otp_user_id", "otp_email", "otp_portal", "otp_masked_email", "otp_sent"]:
            request.session.pop(k, None)
        return redirect(reverse("accounts:login") + "?tab=otp")

    if request.GET.get("resend_otp"):
        user_id = request.session.get("otp_user_id")
        email = request.session.get("otp_email")
        if user_id and email:
            user = User.objects.filter(id=user_id).first()
            if user:
                otp_rec = EmailOTP.generate_otp(email=user.email, user=user)
                try:
                    send_mail(
                        f"{otp_rec.otp} is your FromRythu Login OTP",
                        f"Your new login OTP is: {otp_rec.otp}",
                        getattr(settings, "DEFAULT_FROM_EMAIL", "FromRythu <noreply@fromrythu.com>"),
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f"New OTP sent to {mask_email(user.email)}.")
                except Exception:
                    messages.success(request, f"New OTP generated! (Demo/Dev code: {otp_rec.otp})")
        return redirect(reverse("accounts:login") + "?tab=otp")

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

    otp_sent = request.session.get("otp_sent", False)
    otp_masked_email = request.session.get("otp_masked_email", "")
    active_tab = "otp" if (request.GET.get("tab") == "otp" or otp_sent) else "password"

    return render(
        request,
        "accounts/unified_login.html",
        {
            "form": form,
            "active_tab": active_tab,
            "otp_sent": otp_sent,
            "otp_masked_email": otp_masked_email,
        }
    )


# =====================================================
# FARMER LOGIN (Also handles Admin direct login)
# =====================================================

def farmer_login_view(request):

    if request.user.is_authenticated:

        if request.user.is_admin_role or request.user.role == "admin":
            return redirect("dashboard:admin_dashboard")

        if request.user.role == "farmer":
            return redirect("farmers:dashboard")

        return redirect("dashboard:role_redirect")

    if request.GET.get("cancel_otp"):
        for k in ["otp_user_id", "otp_email", "otp_portal", "otp_masked_email", "otp_sent"]:
            request.session.pop(k, None)
        return redirect(reverse("accounts:farmer_login") + "?tab=otp")

    if request.GET.get("resend_otp"):
        user_id = request.session.get("otp_user_id")
        email = request.session.get("otp_email")
        if user_id and email:
            user = User.objects.filter(id=user_id).first()
            if user:
                otp_rec = EmailOTP.generate_otp(email=user.email, user=user)
                try:
                    send_mail(
                        f"{otp_rec.otp} is your FromRythu Login OTP",
                        f"Your new login OTP is: {otp_rec.otp}",
                        getattr(settings, "DEFAULT_FROM_EMAIL", "FromRythu <noreply@fromrythu.com>"),
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f"New OTP sent to {mask_email(user.email)}.")
                except Exception:
                    messages.success(request, f"New OTP generated! (Demo/Dev code: {otp_rec.otp})")
        return redirect(reverse("accounts:farmer_login") + "?tab=otp")

    if request.method == "POST":

        form = UserLoginForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()

            if user.role == "farmer":

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

            elif user.is_admin_role or user.role == "admin" or user.is_superuser or user.is_staff:

                login(
                    request,
                    user,
                    backend=AUTH_BACKEND
                )

                messages.success(
                    request,
                    f"Welcome back, {user.first_name or user.username}!"
                )

                return redirect("dashboard:admin_dashboard")

            else:

                messages.error(
                    request,
                    "Invalid credentials. Please verify your username and password."
                )

    else:
        form = UserLoginForm()

    otp_sent = request.session.get("otp_sent", False)
    otp_masked_email = request.session.get("otp_masked_email", "")
    active_tab = "otp" if (request.GET.get("tab") == "otp" or otp_sent) else "password"

    return render(
        request,
        "accounts/farmer_login.html",
        {
            "form": form,
            "active_tab": active_tab,
            "otp_sent": otp_sent,
            "otp_masked_email": otp_masked_email,
        }
    )


# =====================================================
# CUSTOMER LOGIN
# =====================================================

def customer_login_view(request):

    if request.user.is_authenticated:

        if request.user.role == "customer":
            return redirect("customers:dashboard")

        return redirect("dashboard:role_redirect")

    if request.GET.get("cancel_otp"):
        for k in ["otp_user_id", "otp_email", "otp_portal", "otp_masked_email", "otp_sent"]:
            request.session.pop(k, None)
        return redirect(reverse("accounts:customer_login") + "?tab=otp")

    if request.GET.get("resend_otp"):
        user_id = request.session.get("otp_user_id")
        email = request.session.get("otp_email")
        if user_id and email:
            user = User.objects.filter(id=user_id).first()
            if user:
                otp_rec = EmailOTP.generate_otp(email=user.email, user=user)
                try:
                    send_mail(
                        f"{otp_rec.otp} is your FromRythu Login OTP",
                        f"Your new login OTP is: {otp_rec.otp}",
                        getattr(settings, "DEFAULT_FROM_EMAIL", "FromRythu <noreply@fromrythu.com>"),
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f"New OTP sent to {mask_email(user.email)}.")
                except Exception:
                    messages.success(request, f"New OTP generated! (Demo/Dev code: {otp_rec.otp})")
        return redirect(reverse("accounts:customer_login") + "?tab=otp")

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

    otp_sent = request.session.get("otp_sent", False)
    otp_masked_email = request.session.get("otp_masked_email", "")
    active_tab = "otp" if (request.GET.get("tab") == "otp" or otp_sent) else "password"

    return render(
        request,
        "accounts/customer_login.html",
        {
            "form": form,
            "active_tab": active_tab,
            "otp_sent": otp_sent,
            "otp_masked_email": otp_masked_email,
        }
    )


# =====================================================
# ADMIN LOGIN (Redirects directly to Farmer Login)
# =====================================================

def admin_login_view(request):
    if request.user.is_authenticated:
        if (
            request.user.is_superuser
            or request.user.is_staff
            or request.user.role == "admin"
        ):
            return redirect("dashboard:admin_dashboard")
        return redirect("dashboard:role_redirect")
    return redirect("accounts:farmer_login")


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
