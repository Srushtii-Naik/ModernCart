from .cart import Cart


def cart_context(request):
    """Makes the current cart's item count available in every template (navbar badge)."""
    cart = Cart(request)
    return {
        'cart_item_count': cart.total_items,
    }
