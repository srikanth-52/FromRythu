from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import User
from products.models import Product
from .models import Message

@login_required
def send_message_view(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content', '').strip()
        product_id = request.POST.get('product_id')

        if not receiver_id or not content:
            messages.error(request, "Message and recipient are required.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        receiver = get_object_or_404(User, id=receiver_id)
        product = Product.objects.filter(id=product_id).first() if product_id else None

        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            product=product,
            content=content
        )
        messages.success(request, f"Your direct message has been sent to {receiver.username}!")

        # Redirect according to role
        if request.user.role == 'farmer':
            return redirect(f"/farmer/messages/?chat_with={receiver.id}")
        elif request.user.role == 'customer':
            return redirect(f"/customer/messages/?chat_with={receiver.id}")
        else:
            return redirect(f"/admin-panel/messages/?chat_with={receiver.id}")

    return redirect('home')
