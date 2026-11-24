from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(
        default=False, 
        help_text="Verification status for Farmers / Accounts"
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_farmer(self):
        return self.role == 'farmer'

    @property
    def is_customer(self):
        return self.role == 'customer'

    @property
    def is_admin_role(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff


class EmailOTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_otps',
        null=True,
        blank=True
    )
    email = models.EmailField(db_index=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Email OTP"
        verbose_name_plural = "Email OTPs"
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.email} ({self.otp}) - Used: {self.is_used}"

    def is_valid(self):
        import datetime
        from django.utils import timezone
        return not self.is_used and (timezone.now() - self.created_at) < datetime.timedelta(minutes=10)

    @classmethod
    def generate_otp(cls, email, user=None):
        import random
        cls.objects.filter(email__iexact=email, is_used=False).update(is_used=True)
        code = f"{random.randint(100000, 999999)}"
        return cls.objects.create(email=email.lower().strip(), user=user, otp=code)
