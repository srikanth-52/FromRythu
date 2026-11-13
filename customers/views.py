from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from accounts.permissions import customer_required
from orders.models import Order, OrderItem
from products.models import Product
from messaging.models import Message
from accounts.models import User
from .models import CustomerProfile

@customer_required
def dashboard_view(request):
    user = request.user
    profile, _ = CustomerProfile.objects.get_or_create(user=user)

    customer_orders = Order.objects.filter(customer=user).order_by('-created_at')
    total_orders = customer_orders.count()
    active_orders = customer_orders.exclude(status__in=['delivered', 'cancelled']).count()
    delivered_orders = customer_orders.filter(status='delivered').count()

    # Recent recommendations from verified farmers
    fresh_produce = Product.objects.filter(is_active=True).select_related('farmer', 'category')[:6]

    context = {
        'profile': profile,
        'customer_orders': customer_orders[:5],
        'total_orders': total_orders,
        'active_orders': active_orders,
        'delivered_orders': delivered_orders,
        'fresh_produce': fresh_produce,
    }
    return render(request, 'customer/dashboard.html', context)


@customer_required
def my_orders_view(request):
    user = request.user
    orders = Order.objects.filter(customer=user).prefetch_related('items', 'payment').order_by('-created_at')
    return render(request, 'customer/my_orders.html', {'orders': orders})


@customer_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    return render(request, 'customer/order_detail.html', {'order': order})


@customer_required
def messages_view(request):
    user = request.user
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        product_id = request.POST.get('product_id')

        if receiver_id and content:
            receiver = get_object_or_404(User, id=receiver_id)
            product = Product.objects.filter(id=product_id).first() if product_id else None
            Message.objects.create(
                sender=user,
                receiver=receiver,
                product=product,
                content=content
            )
            messages.success(request, f"Message sent directly to farmer {receiver.username}!")
            return redirect(f"{request.path}?chat_with={receiver.id}")

    # Messages query
    received = Message.objects.filter(receiver=user).select_related('sender', 'product')
    sent = Message.objects.filter(sender=user).select_related('receiver', 'product')

    received.filter(is_read=False).update(is_read=True)

    contact_ids = set(list(received.values_list('sender_id', flat=True)) + list(sent.values_list('receiver_id', flat=True)))
    contacts = User.objects.filter(id__in=contact_ids)

    selected_contact_id = request.GET.get('chat_with')
    active_chat_contact = None
    chat_thread = []
    if selected_contact_id:
        active_chat_contact = User.objects.filter(id=selected_contact_id).first()
        if active_chat_contact:
            chat_thread = Message.objects.filter(
                (Q(sender=user, receiver=active_chat_contact) |
                 Q(sender=active_chat_contact, receiver=user))
            ).order_by('created_at')

    return render(request, 'customer/messages.html', {
        'contacts': contacts,
        'active_contact': active_chat_contact,
        'chat_thread': chat_thread
    })
