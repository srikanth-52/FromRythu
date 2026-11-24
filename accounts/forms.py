
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)
from django.db import transaction

from farmers.models import FarmerProfile
from customers.models import CustomerProfile

User = get_user_model()


class FarmerRegistrationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="Full Name"
    )

    email = forms.EmailField(
        required=True,
        label="Email Address"
    )

    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label="Phone / Mobile Number"
    )

    farm_name = forms.CharField(
        max_length=200,
        required=True,
        label="Farm Name / Enterprise"
    )

    farm_location = forms.CharField(
        max_length=255,
        required=True,
        label="Farm Address / Location"
    )

    village = forms.CharField(
        max_length=100,
        required=False,
        label="Village"
    )

    district = forms.CharField(
        max_length=100,
        required=False,
        label="District"
    )

    state = forms.CharField(
        max_length=100,
        required=True,
        initial="Telangana",
        label="State"
    )

    farm_size_acres = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        initial=3.0,
        required=True,
        label="Farm Area (Acres)"
    )

    primary_crops = forms.CharField(
        max_length=255,
        required=True,
        label="Main Crops / Produce"
    )

    farming_type = forms.ChoiceField(
        choices=FarmerProfile.FARMING_TYPE_CHOICES,
        required=True,
        label="Farming Practice"
    )

    upi_id = forms.CharField(
        max_length=60,
        required=False,
        label="UPI ID"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "email",
            "phone_number",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email address is already registered."
            )

        return email

    @transaction.atomic
    def save(self, commit=True):

        user = super().save(commit=False)

        user.role = "farmer"
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.state = self.cleaned_data["state"]
        user.city = self.cleaned_data.get("district", "")
        user.address = self.cleaned_data["farm_location"]
        user.is_verified = False

        if commit:
            user.save()

            FarmerProfile.objects.create(
                user=user,
                farm_name=self.cleaned_data["farm_name"],
                farm_location=self.cleaned_data["farm_location"],
                village=self.cleaned_data.get("village", ""),
                district=self.cleaned_data.get("district", ""),
                state=self.cleaned_data["state"],
                farm_size_acres=self.cleaned_data["farm_size_acres"],
                primary_crops=self.cleaned_data["primary_crops"],
                farming_type=self.cleaned_data["farming_type"],
                upi_id=self.cleaned_data.get("upi_id", ""),
            )

        return user


class CustomerRegistrationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="Full Name"
    )

    email = forms.EmailField(
        required=True,
        label="Email Address"
    )

    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label="Contact Phone Number"
    )

    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=True,
        label="Delivery Address"
    )

    city = forms.CharField(
        max_length=100,
        required=True,
        label="City / Town"
    )

    pincode = forms.CharField(
        max_length=10,
        required=True,
        label="Postal PIN Code"
    )

    state = forms.CharField(
        max_length=100,
        initial="Telangana",
        required=True,
        label="State"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "email",
            "phone_number",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email address is already registered."
            )

        return email

    @transaction.atomic
    def save(self, commit=True):

        user = super().save(commit=False)

        user.role = "customer"
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.address = self.cleaned_data["shipping_address"]
        user.city = self.cleaned_data["city"]
        user.pincode = self.cleaned_data["pincode"]
        user.state = self.cleaned_data["state"]
        user.is_verified = True

        if commit:
            user.save()

            CustomerProfile.objects.create(
                user=user,
                default_delivery_address=self.cleaned_data[
                    "shipping_address"
                ],
                city=self.cleaned_data["city"],
                pincode=self.cleaned_data["pincode"],
                state=self.cleaned_data["state"],
            )

        return user


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username or registered email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label="Keep me signed in"
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            clean_user = username.strip()
            # If an email was entered, lookup corresponding username
            if '@' in clean_user:
                matched_user = User.objects.filter(email__iexact=clean_user).first()
                if matched_user:
                    clean_user = matched_user.username
                    self.cleaned_data['username'] = clean_user

            from django.contrib.auth import authenticate
            self.user_cache = authenticate(
                self.request,
                username=clean_user,
                password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "city",
            "state",
            "pincode",
            "profile_picture",
        )
