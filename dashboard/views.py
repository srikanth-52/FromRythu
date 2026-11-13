from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from accounts.permissions import admin_required
from accounts.models import User
from farmers.models import FarmerProfile
from customers.models import CustomerProfile
from products.models import Product, Category, PriceHistory
from inventory.models import StockRecord
from orders.models import Order, OrderItem
from payments.models import Payment
from messaging.models import Message

@login_required
def role_redirect_view(request):
    """
    Central dispatcher to route authenticated users to their corresponding dashboard.
    """
    user = request.user
    if user.is_superuser or user.role == 'admin':
        return redirect('dashboard:admin_dashboard')
    elif user.role == 'farmer':
        return redirect('farmers:dashboard')
    elif user.role == 'customer':
        return redirect('customers:dashboard')
    return redirect('home')


@admin_required
def admin_dashboard_view(request):
    total_farmers = User.objects.filter(role='farmer').count()
    verified_farmers = User.objects.filter(role='farmer', is_verified=True).count()
    pending_farmers = total_farmers - verified_farmers

    total_customers = User.objects.filter(role='customer').count()
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()

    total_orders = Order.objects.count()
    gross_merchandise_value = Order.objects.aggregate(val=Sum('final_amount'))['val'] or 0

    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:8]
    recent_farmers = FarmerProfile.objects.select_related('user').order_by('-created_at')[:6]
    recent_price_updates = PriceHistory.objects.select_related('product').order_by('-created_at')[:5]

    context = {
        'total_farmers': total_farmers,
        'verified_farmers': verified_farmers,
        'pending_farmers': pending_farmers,
        'total_customers': total_customers,
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'gmv': gross_merchandise_value,
        'recent_orders': recent_orders,
        'recent_farmers': recent_farmers,
        'recent_price_updates': recent_price_updates,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def admin_farmers_view(request):
    farmers = FarmerProfile.objects.select_related('user').order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter == 'pending':
        farmers = farmers.filter(is_approved=False)
    elif status_filter == 'approved':
        farmers = farmers.filter(is_approved=True)

    return render(request, 'admin_panel/farmers.html', {
        'farmers': farmers,
        'status_filter': status_filter
    })


@admin_required
def admin_approve_farmer_view(request, farmer_id):
    profile = get_object_or_404(FarmerProfile, id=farmer_id)
    action = request.POST.get('action', 'approve')
    if action == 'approve':
        profile.is_approved = True
        profile.user.is_verified = True
        messages.success(request, f"Farmer {profile.user.username} ({profile.farm_name}) has been verified and approved!")
    else:
        profile.is_approved = False
        profile.user.is_verified = False
        messages.warning(request, f"Farmer {profile.user.username} approval has been revoked.")
    profile.save()
    profile.user.save()
    return redirect('dashboard:admin_farmers')


@admin_required
def admin_customers_view(request):
    customers = User.objects.filter(role='customer').select_related('customer_profile').annotate(
        order_count=Count('customer_orders'),
        total_spent=Sum('customer_orders__final_amount')
    ).order_by('-date_joined')

    return render(request, 'admin_panel/customers.html', {'customers': customers})


@admin_required
def admin_products_view(request):
    products = Product.objects.select_related('farmer', 'category', 'farmer__farmer_profile').order_by('-created_at')
    categories = Category.objects.all()

    cat_filter = request.GET.get('category')
    if cat_filter:
        products = products.filter(category__slug=cat_filter)

    return render(request, 'admin_panel/products.html', {
        'products': products,
        'categories': categories,
        'cat_filter': cat_filter
    })


@admin_required
def admin_inventory_view(request):
    products = Product.objects.select_related('farmer', 'category').all()
    records = StockRecord.objects.select_related('product', 'product__farmer', 'created_by').order_by('-created_at')[:40]

    return render(request, 'admin_panel/inventory.html', {
        'products': products,
        'records': records
    })


@admin_required
def admin_orders_view(request):
    orders = Order.objects.select_related('customer').prefetch_related('items').order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'admin_panel/orders.html', {
        'orders': orders,
        'status_filter': status_filter
    })


@admin_required
def admin_prices_view(request):
    price_logs = PriceHistory.objects.select_related('product', 'product__farmer', 'changed_by').order_by('-created_at')[:50]
    return render(request, 'admin_panel/prices.html', {'price_logs': price_logs})


@admin_required
def admin_messages_view(request):
    messages_list = Message.objects.select_related('sender', 'receiver', 'product', 'order').order_by('-created_at')[:50]
    return render(request, 'admin_panel/messages.html', {'messages_list': messages_list})


@admin_required
def admin_reports_view(request):
    # Category sales
    cat_sales = OrderItem.objects.values('product__category__name').annotate(
        total_revenue=Sum('subtotal'),
        total_items=Sum('quantity')
    ).order_by('-total_revenue')

    # Top selling produce
    top_products = OrderItem.objects.values('product_name', 'unit').annotate(
        revenue=Sum('subtotal'),
        units_sold=Sum('quantity')
    ).order_by('-revenue')[:10]

    # Top performing farmers
    top_farmers = OrderItem.objects.values('farmer__username', 'farmer__farmer_profile__farm_name').annotate(
        revenue=Sum('subtotal'),
        total_orders=Count('order', distinct=True)
    ).order_by('-revenue')[:10]

    total_revenue = Order.objects.aggregate(v=Sum('final_amount'))['v'] or 0

    return render(request, 'admin_panel/reports.html', {
        'cat_sales': cat_sales,
        'top_products': top_products,
        'top_farmers': top_farmers,
        'total_revenue': total_revenue
    })
