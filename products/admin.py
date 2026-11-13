from django.contrib import admin
from .models import Category, Product, PriceHistory, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_class')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'category', 'price_per_unit', 'unit', 'available_stock', 'is_organic', 'is_active', 'featured')
    list_filter = ('category', 'is_organic', 'is_active', 'featured', 'unit')
    search_fields = ('name', 'variety', 'farmer__username', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'old_price', 'new_price', 'reason', 'changed_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'reason')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
