from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """Collects shipping and payment details at checkout."""

    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone', 'address',
            'city', 'state', 'zip_code', 'payment_method',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'you@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 98765 43210'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street address, apartment, etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ZIP / Postal code'}),
            'payment_method': forms.RadioSelect(),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        digits = ''.join(ch for ch in phone if ch.isdigit())
        if len(digits) < 7:
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone
