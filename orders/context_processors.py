def cart_context(request):
    """
    Context processor to inject cart item count and summary across templates.
    """
    if request.user.is_authenticated and getattr(request.user, 'role', '') == 'customer':
        try:
            from orders.models import Cart
            cart = Cart.objects.filter(customer=request.user).first()
            if cart:
                return {
                    'cart_items_count': cart.items.count(),
                    'cart_total_qty': sum(item.quantity for item in cart.items.all()),
                    'cart_subtotal': sum(item.subtotal for item in cart.items.all()),
                }
        except Exception:
            pass
    return {
        'cart_items_count': 0,
        'cart_total_qty': 0,
        'cart_subtotal': 0,
    }

