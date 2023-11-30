from .models import Coupon
from django import forms




class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount', 'expiration_date', 'is_active','minimum_purchase_value','maximum_purchase_value','Usage_count']


        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }