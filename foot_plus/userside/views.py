from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from  catagorie.models import *
from  base.models import *
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from .forms import *
from catagorie.models import *
from orders.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import messages





def is_valid_phone(phone):
    # Phone number should be exactly 10 digits
    phone_pattern = "^\d{10}$"
    return re.match(phone_pattern, str(phone)) is not None

def is_valid_postal_code(postal_code):
    # Postal code should be a valid format based on your requirement
    postal_code_pattern = "^[0-9]{6}$"
    return re.match(postal_code_pattern, postal_code) is not None

def is_not_empty_or_whitespace(value):
    # Check if the value is not empty or contains only whitespace
    return bool(value.strip())











# Create your views here.

@login_required(login_url='base:login')
def profile(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'USER/profile.html', context)


@login_required(login_url='base:login')
def user_orders(request,):
    orders = Order.objects.filter(is_ordered=True, user=request.user).order_by('-created_at')
    print(orders)
   
    context = {
        'orders': orders,
       

    }
    return render(request, 'USER/my_orders.html', context)



@login_required(login_url='base:login')
def cancel_order_product(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'Cancelled':
        order.status = 'Cancelled'
        order.save()
        
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            product = order_product.product.product_id
            product_variants = varients.objects.filter(product_id=product)
                        
            for variant in product_variants:
             variant.stock += order_product.quantity
             variant.save()
            
       
       
    
    return redirect('user:user_dashboard')   

@login_required(login_url='base:login')
def order_details(request, order_id):
    order_products = OrderProduct.objects.filter(order__user=request.user, order__id=order_id)
    orders = Order.objects.filter(is_ordered=True, id=order_id)
    
    payments = Payment.objects.filter(order__id=order_id,user=request.user)

    for order_product in order_products:
        order_product.total = order_product.quantity * order_product.product_price

    context = {
        'order_products': order_products,
        'orders': orders,
        'payments': payments,
    }

    return render(request,'USER/order_detail.html',context)
     
import re
@login_required(login_url='base:login')
def edit_profile(request):
    #user = request.user  # Get the currently logged-in user
    user = Account.objects.get(pk=request.user.pk)
    print("User ID:", user.id)
   
    context={
            'user':user
        }

        
    if request.method == 'POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        username=request.POST.get('user_name')


        username_pattern = "^[a-zA-Z0-9_]+$"
        name_pattern = "^[a-zA-Z]+$"

        if not username or not re.match(username_pattern, username):
            messages.error(request, 'Invalid or empty username. Use only letters, numbers, and underscores.')
        elif not first_name or not re.match(name_pattern, first_name):
            messages.error(request, 'Invalid or empty first name. Use only letters.')
        elif not last_name or not re.match(name_pattern, last_name):
            messages.error(request, 'Invalid or empty last name. Use only letters.')
        else:
         user.first_name=first_name
         user.last_name=last_name
         user.username=username
         user.save()
         return redirect('user:profile')
        
    return render(request, 'USER/edit_profile.html',context)
@login_required(login_url='base:login')
def user_addres(request):
    addresses = Address.objects.filter(user=request.user,is_active=True)
    context = {
        'addresses': addresses
    }
    return render(request, 'USER/user_address.html', context)


@login_required(login_url='base:login')
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
        print(first_name, postal_code)

        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            messages.error(request, 'Invalid or empty first name. Use only letters.')
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            messages.error(request, 'Invalid or empty last name. Use only letters.')
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            messages.error(request, 'Invalid or empty email address.')
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            messages.error(request, 'Invalid or empty phone number. It should be exactly 10 digits.')
        elif not is_not_empty_or_whitespace(address_line_1):
            messages.error(request, 'Address line 1 cannot be empty.')
        elif not is_not_empty_or_whitespace(city):
            messages.error(request, 'City cannot be empty.')
        elif not is_not_empty_or_whitespace(state):
            messages.error(request, 'State cannot be empty.')
        elif not is_valid_postal_code(postal_code):
            messages.error(request, 'Invalid postal code.')
        elif not is_not_empty_or_whitespace(country):
            messages.error(request, 'Country cannot be empty.')
        else:
            address = Address(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                user=request.user
            )
            address.save()
            messages.success(request, 'Address added successfully.')
            # Redirect to the manage addresses page after adding the new address
            return redirect('user:user_address')

    # Add this return statement for the else block
    return render(request, 'USER/add_address.html')

from django.http import JsonResponse
def add_addresss(request):
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

        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            return JsonResponse({'error': 'Invalid or empty first name. Use only letters.'})
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            return JsonResponse({'error': 'Invalid or empty last name. Use only letters.'})
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return JsonResponse({'error': 'Invalid or empty email address.'})
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            return JsonResponse({'error': 'Invalid or empty phone number. It should be exactly 10 digits.'})
        elif not is_not_empty_or_whitespace(address_line_1):
            return JsonResponse({'error': 'Address line 1 cannot be empty.'})
        elif not is_not_empty_or_whitespace(city):
            return JsonResponse({'error': 'City cannot be empty.'})
        elif not is_not_empty_or_whitespace(state):
            return JsonResponse({'error': 'State cannot be empty.'})
        elif not is_valid_postal_code(postal_code):
            return JsonResponse({'error': 'Invalid postal code.'})
        elif not is_not_empty_or_whitespace(country):
            return JsonResponse({'error': 'Country cannot be empty.'})
        else:
            address = Address(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                user=request.user
            )
            address.save()
            return JsonResponse({'success': 'Address added successfully.','redirect_url': reverse('cart:checkout')}) 
            

    return JsonResponse({'error': 'Invalid request method.'})




@login_required(login_url='base:login')
def edit_address(request,id):
    try:
        address = Address.objects.get(pk=id)
    except Address.DoesNotExist:
        messages.error(request, 'Address not found.')
        return redirect('user:user_address')

    if request.method == 'POST':
        # Handle the form submission to edit the address
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

        # Perform validation on the fields
        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            messages.error(request, 'Invalid or empty first name. Use only letters.')
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            messages.error(request, 'Invalid or empty last name. Use only letters.')
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            messages.error(request, 'Invalid or empty email address.')
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            messages.error(request, 'Invalid or empty phone number. It should be exactly 10 digits.')
        elif not is_not_empty_or_whitespace(address_line_1):
            messages.error(request, 'Address line 1 cannot be empty.')
        elif not is_not_empty_or_whitespace(city):
            messages.error(request, 'City cannot be empty.')
        elif not is_not_empty_or_whitespace(state):
            messages.error(request, 'State cannot be empty.')
        elif not is_valid_postal_code(postal_code):
            messages.error(request, 'Invalid postal code.')
        elif not is_not_empty_or_whitespace(country):
            messages.error(request, 'Country cannot be empty.')
        else:
            # All fields are valid, update the address
            address.first_name = first_name
            address.last_name = last_name
            address.email = email
            address.phone = phone
            address.address_line_1 = address_line_1
            address.address_line_2 = address_line_2
            address.city = city
            address.state = state
            address.postal_code = postal_code
            address.country = country

            address.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('user:user_address')

    context = {'address': address}
    return render(request, 'USER/edit_address.html', context)

@login_required(login_url='base:login')
def delete_address(request, id):
    try:
        address = Address.objects.get(id=id)
        address.isactive=False
        address.save()
       
    except Address.DoesNotExist:
     
        pass
    return redirect('user:user_address')


@login_required(login_url='base:login')
def change_password(request):
    if request.method=='POST':
        old_password=request.POST.get('old_password')
        new_password1=request.POST.get('new_password1')
        new_password2=request.POST.get('new_password2')
        user=request.user
        password_pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not user.check_password(old_password):
            messages.error(request,'Old password is incorect')


            
        elif new_password1!=new_password2 :
           messages.error(request,'newpassword desnot match ')
        elif not new_password1 or not re.match(password_pattern,new_password1):
             messages.error(request, 'Invalid or weak password. It should have at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character.')
        else:
            user.set_password(new_password1)
            user.save()
            auth.update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('user:profile')  
    return render(request,'USER/change_password.html')  

    

