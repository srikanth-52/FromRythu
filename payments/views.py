from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from orders.models import Order
from .models import Payment

@login_required
def payment_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    payment = getattr(order, 'payment', None)
    return render(request, 'customer/payment_detail.html', {'order': order, 'payment': payment})
