from django.db import models
from django.conf import settings

class FarmerProfile(models.Model):
    FARMING_TYPE_CHOICES = (
        ('Organic', 'Certified Organic Farming'),
        ('Natural', 'Natural / ZBNF Farming'),
        ('Traditional', 'Traditional Farming'),
        ('Integrated', 'Integrated Pest Management (IPM)'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='farmer_profile'
    )
    farm_name = models.CharField(max_length=200, help_text="e.g. Sri Venkateswara Organic Farms")
    farm_location = models.CharField(max_length=255, help_text="Village / Survey No / Landmark")
    village = models.CharField(max_length=100, blank=True, null=True)
    mandal = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, default='Telangana')
    farm_size_acres = models.DecimalField(max_digits=6, decimal_places=2, default=2.0)
    primary_crops = models.CharField(max_length=255, help_text="e.g. Sona Masoori Paddy, Red Gram, Cotton, Mangoes")
    farming_experience_years = models.PositiveIntegerField(default=5)
    farming_type = models.CharField(max_length=50, choices=FARMING_TYPE_CHOICES, default='Organic')
    
    # Verification & Bank Details
    aadhaar_or_id = models.CharField(max_length=30, blank=True, null=True, help_text="Aadhaar or Kisan Credit Card number")
    id_document = models.FileField(upload_to='farmer_docs/', blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_no = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    upi_id = models.CharField(max_length=60, blank=True, null=True, help_text="Farmer UPI ID for direct customer payment")
    
    is_approved = models.BooleanField(default=False, help_text="Approved by Admin after reviewing credentials")
    bio = models.TextField(blank=True, null=True, help_text="Tell customers about your farm and natural farming practices")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.farm_name} - {self.user.get_full_name() or self.user.username}"
