from django import forms
from .models import FarmerProfile
from products.models import Product, PriceHistory
from inventory.models import StockRecord

class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = [
            'farm_name', 'farm_location', 'village', 'mandal', 'district', 'state',
            'farm_size_acres', 'primary_crops', 'farming_experience_years',
            'farming_type', 'bank_name', 'bank_account_no', 'ifsc_code', 'upi_id', 'bio', 'id_document'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    initial_stock = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        initial=100.0, 
        label="Initial Harvest Stock Quantity",
        help_text="Starting stock available for direct sale"
    )

    class Meta:
        model = Product
        fields = [
            'category', 'name', 'variety', 'description', 'harvest_date',
            'unit', 'price_per_unit', 'mrp', 'min_order_quantity', 'is_organic',
            'image', 'image_url_fallback', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'harvest_date': forms.DateInput(attrs={'type': 'date'}),
        }


class StockForm(forms.ModelForm):
    class Meta:
        model = StockRecord
        fields = ['product', 'transaction_type', 'quantity', 'batch_no', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, farmer=None, **kwargs):
        super().__init__(*args, **kwargs)
        if farmer:
            self.fields['product'].queryset = Product.objects.filter(farmer=farmer)


class PriceChangeForm(forms.Form):
    new_price = forms.DecimalField(max_digits=10, decimal_places=2, label="New Selling Price (₹)")
    reason = forms.CharField(max_length=200, required=False, label="Reason for Price Change", help_text="e.g. Bumper harvest discount, seasonal adjustment")

