from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Product, Category, Order, OrderItem
from .forms import CheckoutForm
from .cart import Cart


def home(request):
    """Landing page: hero, featured products, categories, latest arrivals."""
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.all()
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """Products page with search, category filter, price filter and sorting."""
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()

    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', 'newest')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(short_description__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except Exception:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'total_results': paginator.count,
    }
    return render(request, 'store/products.html', context)


def product_detail(request, slug):
    """Single product page with related products."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def cart_detail(request):
    """Shopping cart page."""
    cart = Cart(request)
    context = {'cart': cart}
    return render(request, 'store/cart.html', context)


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1) or 1)
    cart = Cart(request)
    cart.add(product, quantity)
    messages.success(request, f'"{product.name}" was added to your cart.')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.total_items})
    return redirect(request.META.get('HTTP_REFERER', 'store:cart'))


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1) or 1)
    cart = Cart(request)
    if quantity <= 0:
        cart.remove(product)
        messages.info(request, f'"{product.name}" was removed from your cart.')
    else:
        cart.update(product, quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'subtotal': str(cart.subtotal),
        })
    return redirect('store:cart')


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    messages.info(request, f'"{product.name}" was removed from your cart.')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.total_items})
    return redirect('store:cart')


@login_required(login_url='accounts:login')
def checkout(request):
    """Checkout page - requires authentication."""
    cart = Cart(request)
    if cart.total_items == 0:
        messages.warning(request, 'Your cart is empty. Add some products before checking out.')
        return redirect('store:products')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.subtotal
            order.save()

            for item in cart.items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                )

            cart.clear()
            messages.success(request, 'Your order has been placed successfully!')
            return redirect('store:order_success', order_number=order.order_number)
    else:
        initial = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial)

    context = {'form': form, 'cart': cart}
    return render(request, 'store/checkout.html', context)


@login_required(login_url='accounts:login')
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


def error_404(request, exception=None):
    return render(request, '404.html', status=404)
