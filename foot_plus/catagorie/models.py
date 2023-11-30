from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils.text import slugify
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description=models.TextField(max_length=250,blank=True)
    is_active=models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Category'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('user:product_by_category',args=[self.slug])

    def get_urls(self):
        return reverse('user:filter_product',args=[self.slug])    

    def __str__(self) -> str:
        return self.category_name
        

class Brand(models.Model):
    brand_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=False, null=True, blank=True)
    is_active=models.BooleanField(default=True)


    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.brand_name)
        super(Brand, self).save(*args, **kwargs)

    def __str__(self):
        return self.brand_name
        



class Product(models.Model):
    product_id = models.AutoField(primary_key=True )
    product_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    rprice = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.product_name
    
    def has_variations(self):
        return self.varients.exists()
    
    def is_brand_active(self):
        return self.brand.is_active if self.brand else False

    def is_category_active(self):
        return self.category.is_active if self.category else False

    @property
    def has_variations(self):
        return self.variants.exists()
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('photos/product')

    def __str__(self):
        if self.product:
            return f"Product:{self.product.brand}, {self.product.category}"
        else:
            return "Product: N/A"






class varaitionManager(models.Manager):

   def colors(self):
       return self.filter(is_active=True).values_list('color',flat=True).distinct()

   def sizes(self):
     return self.filter(is_active=True).values_list('size',flat=True).distinct()

   def varients_color(self,color):
    return self.filter(color=color,is_active=True)
   
   def varients_size(self,size):
    return self.filter(size=size,is_active=True)

   
color_choice=[
       ('white','white'),
       ('blue','blue'),
       ('black','black'),
       ('red','red')
   ]

size_choice=[
       (8,8),
       (9,9),
       (10,10),
       (11,11),
   ]  



varation_catagory_choice=(
    ('color','color'),
    ('size','size'),
)  

class varients(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    varation_catagory=models.CharField(max_length=100,choices=varation_catagory_choice)
    color = models.CharField(max_length=100, choices=color_choice)
    size = models.PositiveIntegerField( choices=size_choice)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    price=models.PositiveIntegerField()
    image = models.ImageField(upload_to='varients_images/', null=True, blank=True)

class varientImage(models.Model):
    varients = models.ForeignKey(varients, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('photos/productvarient')

    def __str__(self):
        if self.varients:
            return f"Productvarient:{self.varients.color}, {self.varients.size}"
        else:
            return "Product: N/A"
