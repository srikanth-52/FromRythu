from django.contrib import admin
from .models import StockRecord

@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity', 'batch_no', 'created_by', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('product__name', 'batch_no', 'notes')
