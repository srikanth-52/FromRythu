from django.db import models
from django.conf import settings
from products.models import Product

class StockRecord(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'Stock In (Fresh Harvest / Inward)'),
        ('OUT', 'Stock Out (Sold / Dispatched / Spoilage)'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_records'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='IN')
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Quantity added or deducted in product's base units"
    )
    batch_no = models.CharField(max_length=60, blank=True, null=True, help_text="e.g. BATCH-2026-NOV-01")
    notes = models.TextField(blank=True, null=True, help_text="Reason for entry or storage warehouse details")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = "+" if self.transaction_type == 'IN' else "-"
        return f"{self.product.name}: {sign}{self.quantity} {self.product.unit} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
