from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

class MyAccountManager(BaseUserManager):

    def create_user(self,username,email,first_name,last_name,password=None):
        
        if not email:
            raise ValueError('you must have an email')
        if not username:
            raise ValueError('user must have a username')
        user=self.model(
            email=self.normalize_email(email),# this will neglect the casesensitive
            username=username,
            first_name= first_name,
            last_name=last_name
         )

        user.set_password(password)
        user.save(using=self.db)
        return user
    
    #creating coustom superuser

    def create_superuser(self,username,email,password,first_name,last_name):
        user=self.create_user(
            email=self.normalize_email(email),# this will neglect the casesensitive
            username=username,
            password=password,
            first_name= first_name,
            last_name=last_name
            
            
            

        )

        user.is_admin=True
        user.is_active=True
        user.is_staff=True
        user.is_superadmin=True
        user.save(using=self.db)
        return user



class Account(AbstractBaseUser):
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    username=models.CharField(max_length=50,unique=True)
    email=models.EmailField(max_length=100,unique=True)

    #required
    date_joined =models.DateField(auto_now_add=True)
    last_login=models.DateField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_superadmin=models.BooleanField(default=False)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username','first_name','last_name']
    objects=MyAccountManager()


    def __str__(self) -> str:
        return self.email
    
    def has_perm(self,perm,object=None):
        return self.is_admin
    
    def has_module_perms(self,add_label):
        return True
    

class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    address_type = models.CharField(max_length=10, choices=[('HOME', 'Home'), ('WORK', 'Work')])
    first_name = models.CharField(max_length=100, default=None)
    last_name = models.CharField(max_length=100, default=None)
    email = models.CharField(max_length=100, default=None)
    phone = models.CharField(max_length=10, default=None)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.address_type} - {self.first_name} - {self.address_line_1}"
    