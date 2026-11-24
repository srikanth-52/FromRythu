from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from accounts.permissions import farmer_required
from products.models import Product, PriceHistory, Category
from inventory.models import StockRecord
from orders.models import OrderItem, Order
from messaging.models import Message
from .forms import FarmerProfileForm, ProductForm, StockForm, PriceChangeForm
from .models import FarmerProfile


@farmer_required
def dashboard_view(request):
    user = request.user
    profile, _ = FarmerProfile.objects.get_or_create(
        user=user,
        defaults={
            'farm_name': f"{user.first_name or user.username}'s Farm",
            'farm_location': user.address or 'Telangana',
            'primary_crops': 'Paddy, Pulses'
        }
    )

    farmer_products = Product.objects.filter(farmer=user)
    total_products = farmer_products.count()
    active_products = farmer_products.filter(is_active=True).count()

    order_items = OrderItem.objects.filter(farmer=user)
    total_orders = order_items.values('order').distinct().count()
    pending_orders = order_items.filter(item_status='pending').count()

    # Total revenue from delivered/completed items
    total_revenue = order_items.filter(
        item_status__in=['accepted', 'packed', 'shipped', 'delivered']
    ).aggregate(rev=Sum('subtotal'))['rev'] or 0

    recent_orders = order_items.select_related('order', 'order__customer').order_by('-order__created_at')[:8]
    low_stock_products = [p for p in farmer_products if p.available_stock <= 20]

    context = {
        'profile': profile,
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'farmer_products': farmer_products[:5],
    }
    return render(request, 'farmer/dashboard.html', context)


@farmer_required
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            product.save()

            initial_stock = form.cleaned_data.get('initial_stock', 100.0)
            if initial_stock > 0:
                StockRecord.objects.create(
                    product=product,
                    transaction_type='IN',
                    quantity=initial_stock,
                    batch_no=f"HARVEST-{timezone.now().strftime('%Y%m%d')}",
                    notes="Initial harvest stock added upon product creation",
                    created_by=request.user
                )

            messages.success(
                request,
                f"Produce '{product.name}' has been added with {initial_stock} {product.unit} stock!"
            )
            return redirect('farmers:manage_products')
        else:
            messages.error(request, "Please correct the errors in the product form.")
    else:
        form = ProductForm()

    categories = Category.objects.all().order_by('name')
    return render(
        request,
        'farmer/add_product.html',
        {
            'form': form,
            'is_edit': False,
            'categories': categories,
        }
    )


@farmer_required
def manage_products_view(request):
    products = Product.objects.filter(farmer=request.user).select_related('category')
    return render(request, 'farmer/manage_products.html', {'products': products})


@farmer_required
def edit_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            old_price = product.price_per_unit
            new_p = form.save()
            if old_price != new_p.price_per_unit:
                PriceHistory.objects.create(
                    product=new_p,
                    old_price=old_price,
                    new_price=new_p.price_per_unit,
                    reason="Updated via edit product form",
                    changed_by=request.user
                )
            messages.success(request, f"Produce '{product.name}' updated successfully.")
            return redirect('farmers:manage_products')
        else:
            messages.error(request, "Please correct the errors in the product form.")
    else:
        form = ProductForm(
            instance=product,
            initial={'initial_stock': product.available_stock}
        )

    categories = Category.objects.all().order_by('name')
    return render(
        request,
        'farmer/add_product.html',
        {
            'form': form,
            'is_edit': True,
            'product': product,
            'categories': categories,
        }
    )

@farmer_required
def toggle_product_active_view(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    product.is_active = not product.is_active
    product.save()
    status_str = "Active" if product.is_active else "Hidden/Inactive"
    messages.info(request, f"Status of '{product.name}' changed to {status_str}.")
    return redirect('farmers:manage_products')


@farmer_required
def stock_view(request):
    user = request.user
    user_products = Product.objects.filter(farmer=user)
    stock_records = StockRecord.objects.filter(product__farmer=user).select_related('product').order_by('-created_at')

    if request.method == 'POST':
        form = StockForm(request.POST, farmer=user)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = user
            record.save()
            messages.success(
                request,
                f"Stock record added: {record.get_transaction_type_display()} ({record.quantity} {record.product.unit}) for {record.product.name}."
            )
            return redirect('farmers:stock')
    else:
        form = StockForm(farmer=user)

    return render(request, 'farmer/stock.html', {
        'form': form,
        'user_products': user_products,
        'stock_records': stock_records[:30]
    })


@farmer_required
def price_view(request):
    user = request.user
    user_products = Product.objects.filter(farmer=user)
    price_logs = PriceHistory.objects.filter(product__farmer=user).select_related('product').order_by('-created_at')[:25]

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id, farmer=user)
        new_price = request.POST.get('new_price')
        reason = request.POST.get('reason', 'Market adjustment')

        if new_price:
            try:
                new_price_dec = float(new_price)
                old_p = product.price_per_unit
                product.price_per_unit = new_price_dec
                product.save()
                PriceHistory.objects.create(
                    product=product,
                    old_price=old_p,
                    new_price=new_price_dec,
                    reason=reason,
                    changed_by=user
                )
                messages.success(
                    request,
                    f"Price of {product.name} updated from ₹{old_p} to ₹{new_price_dec}/{product.unit}."
                )
            except ValueError:
                messages.error(request, "Invalid price entered.")
        return redirect('farmers:price')

    return render(request, 'farmer/price.html', {
        'user_products': user_products,
        'price_logs': price_logs
    })


@farmer_required
def orders_view(request):
    user = request.user
    order_items = OrderItem.objects.filter(farmer=user).select_related('order', 'order__customer', 'product').order_by('-order__created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        order_items = order_items.filter(item_status=status_filter)

    return render(request, 'farmer/orders.html', {
        'order_items': order_items,
        'selected_status': status_filter
    })


@farmer_required
def update_item_status_view(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, farmer=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(OrderItem.ITEM_STATUS_CHOICES):
            item.item_status = new_status
            item.save()

            # If all items in this order are updated, update the main order status too
            order = item.order
            all_statuses = set(order.items.values_list('item_status', flat=True))
            if all_statuses == {'delivered'}:
                order.status = 'delivered'
                order.save()
            elif all_statuses == {'shipped'}:
                order.status = 'shipped'
                order.save()
            elif all_statuses == {'packed'}:
                order.status = 'packed'
                order.save()
            elif 'accepted' in all_statuses and order.status == 'pending':
                order.status = 'accepted'
                order.save()

            messages.success(
                request,
                f"Order #{item.order.order_number} item '{item.product_name}' status updated to {item.get_item_status_display()}."
            )
    return redirect('farmers:orders')


@farmer_required
def messages_view(request):
    user = request.user
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        if receiver_id and content:
            from accounts.models import User as AppUser
            receiver = get_object_or_404(AppUser, id=receiver_id)
            Message.objects.create(
                sender=user,
                receiver=receiver,
                content=content
            )
            messages.success(request, f"Reply sent to {receiver.username}!")
            return redirect('farmers:messages')

    # All conversations involving this farmer
    received = Message.objects.filter(receiver=user).select_related('sender', 'product', 'order')
    sent = Message.objects.filter(sender=user).select_related('receiver', 'product', 'order')
    all_msgs = (received | sent).order_by('created_at')

    # Mark received as read
    received.filter(is_read=False).update(is_read=True)

    contact_ids = set(
        list(received.values_list('sender_id', flat=True)) +
        list(sent.values_list('receiver_id', flat=True))
    )
    from accounts.models import User as AppUser
    contacts = AppUser.objects.filter(id__in=contact_ids)

    selected_contact_id = request.GET.get('chat_with')
    active_chat_contact = None
    chat_thread = []
    if selected_contact_id:
        active_chat_contact = AppUser.objects.filter(id=selected_contact_id).first()
        if active_chat_contact:
            chat_thread = Message.objects.filter(
                (Q(sender=user, receiver=active_chat_contact) |
                 Q(sender=active_chat_contact, receiver=user))
            ).order_by('created_at')

    return render(request, 'farmer/messages.html', {
        'contacts': contacts,
        'active_contact': active_chat_contact,
        'chat_thread': chat_thread,
        'all_msgs': all_msgs
    })


@farmer_required
def sales_report_view(request):
    user = request.user
    items = OrderItem.objects.filter(farmer=user).select_related('order', 'product')

    product_sales = items.values('product_name', 'unit').annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum('subtotal'),
        order_count=Count('id')
    ).order_by('-total_revenue')

    total_gross = sum(p['total_revenue'] or 0 for p in product_sales)
    total_qty_sold = sum(p['total_qty'] or 0 for p in product_sales)

    return render(request, 'farmer/sales_report.html', {
        'product_sales': product_sales,
        'total_gross': total_gross,
        'total_qty_sold': total_qty_sold,
        'items': items[:20]
    })
