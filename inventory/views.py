from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import StockRecord

@login_required
def stock_history_api(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not (request.user == product.farmer or request.user.is_superuser or request.user.role == 'admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    records = StockRecord.objects.filter(product=product).order_by('-created_at')[:20]
    data = [
        {
            'id': r.id,
            'type': r.transaction_type,
            'quantity': float(r.quantity),
            'batch_no': r.batch_no or '',
            'notes': r.notes or '',
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for r in records
    ]
    return JsonResponse({'product': product.name, 'available_stock': product.available_stock, 'records': data})
