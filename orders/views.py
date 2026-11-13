from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from products.models import Product
from inventory.models import StockRecord
from payments.models import Payment
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    items = cart.items.select_related('product', 'product__farmer').all()
    subtotal = cart.total_price
    delivery_fee = 0 if subtotal >= 500 or subtotal == 0 else 50
    total = subtotal + delivery_fee

    return render(request, 'customer/cart.html', {
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
    })


@login_required
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if request.user.role == 'farmer' and request.user == product.farmer:
        messages.warning(request, "Farmers cannot purchase their own listed produce.")
        return redirect('products:detail', slug=product.slug)

    try:
        quantity = float(request.POST.get('quantity', 1.0))
    except (ValueError, TypeError):
        quantity = 1.0

    if quantity < float(product.min_order_quantity):
        messages.error(request, f"Minimum order quantity for {product.name} is {product.min_order_quantity} {product.unit}.")
        return redirect('products:detail', slug=product.slug)

    if product.available_stock < quantity:
        messages.error(request, f"Sorry, only {product.available_stock} {product.unit} is currently in stock.")
        return redirect('products:detail', slug=product.slug)

    cart, _ = Cart.objects.get_or_create(customer=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        new_qty = float(cart_item.quantity) + quantity
        if new_qty > product.available_stock:
            messages.error(request, f"Cannot add more. Total in cart ({new_qty} {product.unit}) exceeds available stock.")
            return redirect('orders:cart')
        cart_item.quantity = new_qty
    else:
        cart_item.quantity = quantity

    cart_item.save()
    messages.success(request, f"Added {quantity} {product.unit} of '{product.name}' directly to your cart!")

    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('orders:cart')


@login_required
def update_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            qty = float(request.POST.get('quantity', cart_item.quantity))
        except (ValueError, TypeError):
            qty = float(cart_item.quantity)

        if action == 'increase':
            qty += 1.0
        elif action == 'decrease':
            qty = max(float(cart_item.product.min_order_quantity), qty - 1.0)

        if qty > cart_item.product.available_stock:
            messages.error(request, f"Stock limit reached ({cart_item.product.available_stock} {cart_item.product.unit}).")
        else:
            cart_item.quantity = qty
            cart_item.save()
            messages.success(request, f"Updated {cart_item.product.name} quantity to {qty} {cart_item.product.unit}.")

    return redirect('orders:cart')


@login_required
def remove_from_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f"Removed '{product_name}' from your cart.")
    return redirect('orders:cart')


@login_required
def checkout_view(request):
    cart = Cart.objects.filter(customer=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, "Your cart is empty. Please select farm produce before checking out.")
        return redirect('products:list')

    items = cart.items.select_related('product', 'product__farmer').all()

    # Pre-check stock
    for item in items:
        if item.quantity > item.product.available_stock:
            messages.error(request, f"Produce '{item.product.name}' only has {item.product.available_stock} {item.product.unit} available. Please adjust your cart.")
            return redirect('orders:cart')

    subtotal = cart.total_price
    delivery_fee = 0 if subtotal >= 500 else 50
    final_total = subtotal + delivery_fee

    user = request.user
    customer_profile = getattr(user, 'customer_profile', None)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.customer = user
                order.total_amount = subtotal
                order.delivery_fee = delivery_fee
                order.final_amount = final_total
                order.status = 'pending'

                payment_method = form.cleaned_data['payment_method']
                order.payment_status = 'completed' if payment_method in ['CARD', 'UPI'] else 'pending'
                order.save()

                # Create OrderItems and Deduct Stock via StockRecord
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        farmer=item.product.farmer,
                        product_name=item.product.name,
                        unit=item.product.unit,
                        unit_price=item.product.price_per_unit,
                        quantity=item.quantity,
                        subtotal=item.subtotal,
                        item_status='pending'
                    )

                    # Deduct inventory stock
                    StockRecord.objects.create(
                        product=item.product,
                        transaction_type='OUT',
                        quantity=item.quantity,
                        batch_no=f"ORD-{order.order_number}",
                        notes=f"Order fulfillment for Order #{order.order_number}",
                        created_by=user
                    )

                # Create Payment Record
                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=final_total,
                    status='completed' if payment_method in ['CARD', 'UPI'] else 'pending',
                    paid_at=timezone.now() if payment_method in ['CARD', 'UPI'] else None,
                    payment_notes=f"Method: {payment_method}"
                )

                # Clear cart
                cart.items.all().delete()

            messages.success(request, f"Order #{order.order_number} placed successfully directly with the farmers!")
            return redirect('orders:order_success', order_number=order.order_number)
    else:
        initial_data = {
            'shipping_full_name': user.get_full_name() or user.username,
            'shipping_phone': user.phone_number or '',
            'shipping_address': (customer_profile.default_delivery_address if customer_profile else user.address) or '',
            'shipping_city': user.city or '',
            'shipping_state': user.state or 'Telangana',
            'shipping_pincode': user.pincode or '',
        }
        form = CheckoutForm(initial=initial_data)

    return render(request, 'customer/checkout.html', {
        'form': form,
        'items': items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'final_total': final_total,
    })


@login_required
def order_success_view(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items', 'payment'), order_number=order_number, customer=request.user)
    return render(request, 'customer/order_success.html', {'order': order})


@login_required
def order_track_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if not (order.customer == request.user or request.user.role in ['admin', 'farmer'] or request.user.is_superuser):
        messages.error(request, "Unauthorized access to order details.")
        return redirect('home')

    return render(request, 'customer/order_detail.html', {'order': order})
