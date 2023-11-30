from django.shortcuts import render,HttpResponse,redirect
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from catagorie.models import *
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.conf import settings
import random 
from store.models import *

# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    
    products = Product.objects.filter(
    varients__isnull=False,
    is_active=True,
    brand__is_active=True, 
    category__is_active=True).distinct()               
    
    categories=Category.objects.filter(is_active=True)
    banner=Banner.objects.filter(set=True)
    if banner==None : banner=[None]
    print(banner)

    context={
        'banner':banner,
        'products': products,
        'categories': categories
    }
    return render(request,'USER/index.html',context)


def product_info(request):
    return render(request,'user/product.html')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def handlelogin(request):
    if request.user.is_authenticated:
        return redirect('base:index')
    
    if request.method=='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)

        if not Account.objects.filter(email=email).exists():
            messages.error(request, "Invalid Email Adress")
            return redirect('base:login')
        
        if not Account.objects.filter(email=email,is_active=True).exists():
            messages.error(request, "You are blocked by admin ! Please contact admin ")
            return redirect('base:login') 
        
        user = authenticate(email=email,password=password)
        print(user)
        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('base:login')
        else:
            login(request,user)
            messages.success(request, "sigin successful!")
            return redirect('base:index')


    return render(request,'USER/login_page.html')


def user_logout(request):
 if request.user.is_authenticated:  
    logout(request)
    messages.success(request, "logout successful!")
    return redirect('base:login')




import re
from django.contrib.auth.password_validation import validate_password, ValidationError

def handlesignup(request):
    if request.user.is_authenticated:
        return redirect('base:index')
    if request.method == 'POST':
        # Get the data from the form
        first_name = request.POST.get("firstname")
        last_name = request.POST.get("lastname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("password")
        pass2 = request.POST.get("password1")

        # Validate input using regular expressions
        if not re.match(r'^\w+$', username):
            messages.error(request, "Username can only contain alphanumeric characters and underscores.")
            return redirect('base:signup')

        if not re.match(r'^[a-zA-Z]+$', first_name) or not re.match(r'^[a-zA-Z]+$', last_name):
            messages.error(request, "First name and last name can only contain alphabetical characters.")
            return redirect('base:signup')

        # Check for existing email
        if Account.objects.filter(email=email).exists():
            messages.error(request, "Email address already exists.")
            return redirect('base:signup')

        # Check for password match
        if pass1 != pass2:
            messages.error(request, "Password mismatch.")
            return redirect('base:signup')

        # Check for empty spaces in the password
        if ' ' in pass1 or ' ' in pass2:
            messages.error(request, "Password cannot contain empty spaces.")
            return redirect('base:signup')

        # Validate password strength
        try:
            validate_password(pass1)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect('base:signup')

        # Create user
        user = Account.objects.create_user(email=email, password=pass1, username=username, first_name=first_name, last_name=last_name)
        user.save()
        request.session['email'] = email

        return redirect('base:sp')

    return render(request, "USER/signuppage.html")
 


def sent_otp(request):
    randomn=random.randint(1000,9999)
    request.session['otpn']=randomn

    send_mail(
     "OTP AUTHENTICATING fKart",
     f"{randomn} -OTP",
     "algo23196@gmail.com",
     [request.session['email']],
     fail_silently=False,
      )
    return redirect('base:vp')

def veify_otp(request):
  user=Account.objects.get(email=request.session['email'])
  if request.method=="POST":
      if str(request.session['otpn'])!= str(request.POST['otp']):
          messages.error(request,"invalid otp")

      else:
         user.is_active=True
         user.save()
         login(request,user)
         messages.success(request, "signup successful!")
         return redirect('base:index')
  return render(request,'user/otp_veification.html')



def resend_otp(request):
    
    if request.user.is_authenticated:
        return redirect('account:index')
    
    email = request.session.get('email')
    print(email)
    if email is None:
        email=request.user.email
    print(email)    
    random_num = random.randint(1000, 9999)
    request.session['otpn'] = random_num
    send_mail(
        "Resend OTP for fKart",
        f"{random_num} - OTP",
        "algo23196@gmail.com",
        [email],
        fail_silently=False,
    )
    messages.success(request, "OTP has been resent successfully!")
    return redirect('base:vp')       


def base(request):
    return render(request,'ADMIN/index.html')



def admin_login(request):

    if request.user.is_authenticated:
        if request.user.is_superadmin:
            return redirect('catagorie:dashboard')

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        print(email,password)
        user = authenticate(email=email, password=password)
        if user:
            if user.is_superadmin:
                login(request, user)
                print('fghjk')
                messages.success(request, "Admin login successful!")
                return redirect('catagorie:dashboard')  
        else:
             messages.error(request, "Invalid admin credentials!")


    return render(request, 'ADMIN/login.html')


def admin_logout(request):
  if request.user.is_superadmin:
    logout(request)
    return redirect('base:admin_pannel')



#base page
def db(request):
    return render(request,'admin/inheritance.html')

#product click
def product_detail(request,product_id):
    try:
        product = Product.objects.get(pk=product_id)
        product_variants = varients.objects.filter(product=product ,is_active=True)
        distinct_colors = product_variants.values('color').distinct()
        distinct_size=product_variants.values('size').distinct()
        print(distinct_size)

        selected_color = request.GET.get('selected_color', None)
        selected_variants = None
        print(selected_color)
        if selected_color:
            selected_variants = varients.objects.filter(product=product, color=selected_color)
            print(selected_color)

            for variant in selected_variants:
                 print(variant.images.all()) 

    except Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)

    context = {
        'products': product,
        'product_variants': product_variants,
        'distinct_colors': distinct_colors,
        'distinct_size':distinct_size,
        'selected_color': selected_color,
        'selected_variants': selected_variants,
    }
    return render(request,'user/product.html',context)




def add_address(request):
    if request.method == 'POST':
        # Handle the form submission to add a new address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        print(first_name,postal_code)
        # Create a new Address object and save it to the database
        address = Address(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code= postal_code,
            country=country,
            user=request.user  # Assuming you have implemented authentication
         )
        address.save()

        # Redirect to the manage addresses page after adding the new address
        return redirect('cart:checkout')

    
    return render(request, 'user/add address.html',)


        

