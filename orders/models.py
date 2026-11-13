from django.db import models
from django.conf import settings
from products.models import Product
import uuid

class Cart(models.Model):
    customer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.customer.username}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1.0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} {self.product.unit} of {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.product.price_per_unit


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Order Placed (Pending Confirmation)'),
        ('accepted', 'Accepted by Farmer'),
        ('packed', 'Freshly Harvested & Packed'),
        ('shipped', 'Dispatched / In Transit'),
        ('delivered', 'Delivered Successfully'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Payment Pending'),
        ('completed', 'Payment Completed'),
        ('failed', 'Payment Failed'),
        ('cod', 'Cash on Delivery Verified'),
    )

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders'
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Shipping details
    shipping_full_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100, default='Telangana')
    shipping_pincode = models.CharField(max_length=10)
    delivery_instructions = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"RYTHU-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - ₹{self.final_amount} ({self.get_status_display()})"


class OrderItem(models.Model):
    ITEM_STATUS_CHOICES = (
        ('pending', 'Pending Confirmation'),
        ('accepted', 'Accepted'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='farmer_orders'
    )
    product_name = models.CharField(max_length=200)
    unit = models.CharField(max_length=30)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    item_status = models.CharField(max_length=20, choices=ITEM_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.product_name} x {self.quantity} {self.unit} (Order #{self.order.order_number})"
