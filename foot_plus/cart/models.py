from django.db import models
from catagorie.models import *
from base.models import *
from orders.models import *


# Create your models here.
class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    date_added=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    is_active=models.BooleanField(default=True)
    variations = models.ForeignKey(varients, on_delete=models.CASCADE, null=True)

    def sub_total(self):
        return self.variations.price * self.quantity

    def __str__(self):
        return self.product.product_name
    

class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=50, blank=True)
    discount = models.PositiveIntegerField(help_text="Discount percentage")
    expiration_date = models.DateField()
    minimum_purchase_value = models.PositiveIntegerField(blank=False,default=1000)
    maximum_purchase_value = models.PositiveIntegerField(blank=False,default=10000)
    Usage_count=models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def RedeemedCoupon(self, user):
        redeemed_details = RedeemedCoupon.objects.filter(coupon=self, user=user, is_redeemed=True)
        return redeemed_details.exists()
    def validate_usage_count(self, user):
        if self.Usage_count is not None:
            redeemed_count = RedeemedCoupon.objects.filter(coupon=self, user=user, is_redeemed=True).count()
            return redeemed_count < self.Usage_count
        return True
    
class RedeemedCoupon(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    redeemed_date = models.DateTimeField(auto_now_add=True)
    is_redeemed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.coupon.code} redeemed by {self.user.username} on {self.redeemed_date}"