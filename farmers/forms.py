
from django import forms
from django.utils.text import slugify
from .models import FarmerProfile
from products.models import Product, PriceHistory, Category
from inventory.models import StockRecord


class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = [
            'farm_name',
            'farm_location',
            'village',
            'mandal',
            'district',
            'state',
            'farm_size_acres',
            'primary_crops',
            'farming_experience_years',
            'farming_type',
            'bank_name',
            'bank_account_no',
            'ifsc_code',
            'upi_id',
            'bio',
            'id_document'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }


class ProductForm(forms.ModelForm):

    # Manual category input instead of dropdown
    category = forms.CharField(
        max_length=100,
        required=True,
        label="Produce Category",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Rice, Vegetables, Fruits, Pulses'
        })
    )

    initial_stock = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=100.0,
        required=True,
        label="Initial Harvest Stock Quantity",
        help_text="Starting stock available for direct sale"
    )

    class Meta:
        model = Product

        # Category is handled separately because it is a ForeignKey.
        exclude = ['category']

        fields = [
            'name',
            'variety',
            'description',
            'harvest_date',
            'unit',
            'price_per_unit',
            'mrp',
            'min_order_quantity',
            'is_organic',
            'image',
            'image_url_fallback',
            'is_active'
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'harvest_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show the existing category when editing
        if self.instance and self.instance.pk and self.instance.category:
            self.initial['category'] = self.instance.category.name

    def clean_category(self):
        category_name = self.cleaned_data.get('category', '').strip()

        if not category_name:
            raise forms.ValidationError(
                "Please enter a produce category."
            )

        return category_name

    def save(self, commit=True):
        product = super().save(commit=False)

        category_name = self.cleaned_data.get('category', '').strip()

        # Get existing category or create a new category
        category = Category.objects.filter(name__iexact=category_name).first()
        if not category:
            base_slug = slugify(category_name) or "produce"
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            category = Category.objects.create(name=category_name, slug=slug)

        product.category = category

        if commit:
            product.save()
            self.save_m2m()

        return product


class StockForm(forms.ModelForm):

    class Meta:
        model = StockRecord
        fields = [
            'product',
            'transaction_type',
            'quantity',
            'batch_no',
            'notes'
        ]

        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, farmer=None, **kwargs):
        super().__init__(*args, **kwargs)

        if farmer:
            self.fields['product'].queryset = Product.objects.filter(
                farmer=farmer
            )


class PriceChangeForm(forms.Form):

    new_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="New Selling Price (₹)"
    )

    reason = forms.CharField(
        max_length=200,
        required=False,
        label="Reason for Price Change",
        help_text="e.g. Bumper harvest discount, seasonal adjustment"
    )
