from django.db import models
from django.conf import settings

class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )
    default_delivery_address = models.TextField(blank=True, null=True)
    landmark = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, default='Telangana')
    pincode = models.CharField(max_length=10, blank=True, null=True)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    dietary_preference = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        choices=[
            ('Organic Preferred', 'Strictly Organic'),
            ('Direct Farm Fresh', 'Farm Fresh General'),
            ('Bulk Grain Buyer', 'Bulk Grain Buyer / Household'),
        ],
        default='Direct Farm Fresh'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} (Customer)"
