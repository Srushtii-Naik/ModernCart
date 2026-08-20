from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from .forms import RegisterForm, LoginForm
from store.models import Order
from store.cart import Cart


def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to ModernCart, {user.first_name or user.username}! Your account has been created.')
            return redirect('store:home')
        else:
            messages.error(request, 'Please fix the errors below and try again.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


class ModernLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        # Merge any items added to the cart while browsing as a guest.
        Cart.merge_session_cart_into_user(self.request, self.request.user)
        messages.success(self.request, f'Welcome back, {self.request.user.first_name or self.request.user.username}!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


@login_required(login_url='accounts:login')
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('store:home')


@login_required(login_url='accounts:login')
def dashboard_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')[:20]
    context = {
        'orders': orders,
        'order_count': Order.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)
