from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery (Pay directly to farmer upon receiving produce)'),
        ('UPI', 'Direct UPI Transfer (GPay / PhonePe / Paytm to Farmer Account)'),
        ('CARD', 'Online Payment / Card / NetBanking (Instant Confirmation)'),
    )

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial='COD'
    )

    class Meta:
        model = Order
        fields = [
            'shipping_full_name', 'shipping_phone', 'shipping_address',
            'shipping_city', 'shipping_state', 'shipping_pincode', 'delivery_instructions'
        ]
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'House/Flat No, Street, Landmark'}),
            'delivery_instructions': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional delivery notes for farmer / delivery partner'}),
        }

