from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon_class = models.CharField(max_length=50, default='bi-basket', help_text="Bootstrap icon class e.g. bi-basket, bi-flower1")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "category"
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = (
        ('kg', 'Kilogram (kg)'),
        ('quintal', 'Quintal (100 kg)'),
        ('bag_25kg', 'Bag (25 kg)'),
        ('bag_50kg', 'Bag (50 kg)'),
        ('bunch', 'Bunch / Dozen'),
        ('litre', 'Litre (L)'),
    )

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='farmer_products'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    variety = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. BPT 5204 Sona Masoori, Guntur Sannam")
    description = models.TextField()
    harvest_date = models.DateField(blank=True, null=True, help_text="Date of recent harvest")
    unit = models.CharField(max_length=30, choices=UNIT_CHOICES, default='kg')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Farmer direct selling price (Rs.)")
    mrp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Retail market comparison price")
    min_order_quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1.0)
    is_organic = models.BooleanField(default=True, help_text="Grown without synthetic pesticides/chemical fertilizers")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url_fallback = models.CharField(max_length=500, blank=True, null=True, help_text="Fallback photo URL for demo and high quality farm pics")
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - ₹{self.price_per_unit}/{self.unit} ({self.farmer.username})"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url_fallback:
            return self.image_url_fallback
        return "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=600&q=80"

    @property
    def available_stock(self):
        try:
            from inventory.models import StockRecord
            records = StockRecord.objects.filter(product=self)
            stock_in = sum(r.quantity for r in records if r.transaction_type == 'IN')
            stock_out = sum(r.quantity for r in records if r.transaction_type == 'OUT')
            return max(0.0, float(stock_in - stock_out))
        except Exception:
            return 0.0

    @property
    def direct_savings_percentage(self):
        if self.mrp and self.mrp > self.price_per_unit:
            return int(((self.mrp - self.price_per_unit) / self.mrp) * 100)
        return 0


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. Market fluctuation, Fresh yield surplus")
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name}: ₹{self.old_price} -> ₹{self.new_price} on {self.created_at.strftime('%Y-%m-%d')}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5, choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.username} on {self.product.name} ({self.rating}★)"
