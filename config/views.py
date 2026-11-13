from django.shortcuts import render, redirect
from products.models import Product, Category
from farmers.models import FarmerProfile

def home_view(request):
    featured_products = Product.objects.filter(is_active=True, featured=True).select_related('farmer', 'category')[:8]
    if not featured_products.exists():
        featured_products = Product.objects.filter(is_active=True).select_related('farmer', 'category')[:8]

    latest_harvest = Product.objects.filter(is_active=True).select_related('farmer', 'category').order_by('-created_at')[:8]
    categories = Category.objects.all()[:8]
    verified_farmers = FarmerProfile.objects.filter(is_approved=True).select_related('user')[:4]

    return render(request, 'home.html', {
        'featured_products': featured_products,
        'latest_harvest': latest_harvest,
        'categories': categories,
        'verified_farmers': verified_farmers,
    })

def global_messages_redirect(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.user.role == 'farmer':
        return redirect('farmers:messages')
    elif request.user.role == 'customer':
        return redirect('customers:messages')
    elif request.user.role == 'admin' or request.user.is_superuser:
        return redirect('dashboard:admin_messages')
    return redirect('home')

