from django.db import models
from base.models import *
from catagorie.models import *
from django.utils import  timezone

# Create your models here.
class wallet(models.Model):
    user=models.ForeignKey(Account, on_delete=models.CASCADE)
    wallet_amount=models.FloatField(default=100)
    created_on=models.DateField(auto_now=True)

    def __str__(self):
        return(self.user.username,self.wallet_amount)


class WishList(models.Model):
	user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
	date_added = models.DateField(default=timezone.now)        