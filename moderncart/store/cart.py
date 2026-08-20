"""
Session/user-aware shopping cart helper.

Wraps the Cart and CartItem database models so that both anonymous
visitors (identified by their session key) and logged-in users get a
persistent cart, backed by the database rather than only the session.
"""
from .models import Cart as CartModel, CartItem, Product


class Cart:
    def __init__(self, request):
        self.request = request
        if request.user.is_authenticated:
            cart_obj, _ = CartModel.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart_obj, _ = CartModel.objects.get_or_create(session_key=session_key, user=None)
        self.cart = cart_obj

    def add(self, product: Product, quantity: int = 1):
        item, created = CartItem.objects.get_or_create(cart=self.cart, product=product)
        if created:
            item.quantity = quantity
        else:
            item.quantity += quantity
        item.quantity = max(1, min(item.quantity, product.stock or item.quantity))
        item.save()
        return item

    def update(self, product: Product, quantity: int):
        quantity = max(1, quantity)
        CartItem.objects.filter(cart=self.cart, product=product).update(quantity=quantity)

    def remove(self, product: Product):
        CartItem.objects.filter(cart=self.cart, product=product).delete()

    def clear(self):
        self.cart.items.all().delete()

    @property
    def items(self):
        return self.cart.items.select_related('product').all()

    @property
    def total_items(self):
        return self.cart.total_items

    @property
    def subtotal(self):
        return self.cart.subtotal

    @staticmethod
    def merge_session_cart_into_user(request, user):
        """Called right after login: move any anonymous session cart items
        into the now-authenticated user's cart, then discard the old cart."""
        session_key = request.session.session_key
        if not session_key:
            return
        try:
            anon_cart = CartModel.objects.get(session_key=session_key, user=None)
        except CartModel.DoesNotExist:
            return
        user_cart, _ = CartModel.objects.get_or_create(user=user)
        for item in anon_cart.items.all():
            existing = CartItem.objects.filter(cart=user_cart, product=item.product).first()
            if existing:
                existing.quantity += item.quantity
                existing.save()
            else:
                item.cart = user_cart
                item.save()
        anon_cart.delete()
