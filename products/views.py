from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Product, Category, PriceHistory, Review

def product_list_view(request):
    products = Product.objects.filter(is_active=True).select_related('farmer', 'category', 'farmer__farmer_profile')
    categories = Category.objects.all()

    # Search query
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(variety__icontains=query) |
            Q(farmer__farmer_profile__farm_name__icontains=query) |
            Q(farmer__city__icontains=query)
        )

    # Category filter
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # Farming type / Organic filter
    organic = request.GET.get('organic')
    if organic == '1':
        products = products.filter(is_organic=True)

    # Price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price_per_unit__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price_per_unit__lte=float(max_price))
        except ValueError:
            pass

    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['price_asc', 'price_per_unit']:
        products = products.order_by('price_per_unit')
    elif sort_by in ['price_desc', '-price_per_unit']:
        products = products.order_by('-price_per_unit')
    elif sort_by == 'harvest':
        products = products.order_by('-harvest_date')
    else:
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customer/products.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'organic': organic,
        'sort_by': sort_by,
        'total_count': paginator.count,
    })


def product_detail_view(request, slug):
    product = get_object_or_404(Product.objects.select_related('farmer', 'category', 'farmer__farmer_profile'), slug=slug)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    price_logs = PriceHistory.objects.filter(product=product).order_by('-created_at')[:10]
    reviews = product.reviews.select_related('customer').order_by('-created_at')

    # Review submission
    if request.method == 'POST' and request.user.is_authenticated:
        if request.user.role == 'customer' or request.user.is_superuser:
            rating = request.POST.get('rating', 5)
            comment = request.POST.get('comment', '').strip()
            if comment:
                Review.objects.create(
                    product=product,
                    customer=request.user,
                    rating=int(rating),
                    comment=comment
                )
                messages.success(request, "Thank you! Your verified review has been published.")
                return redirect('products:detail', slug=product.slug)

    farmer_profile = getattr(product.farmer, 'farmer_profile', None)

    return render(request, 'customer/product_details.html', {
        'product': product,
        'related_products': related_products,
        'price_logs': price_logs,
        'reviews': reviews,
        'farmer_profile': farmer_profile,
    })
