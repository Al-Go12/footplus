from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from  catagorie.models import *
from  base.models import Account
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import *
from orders.models import *
from django.http import HttpResponseBadRequest
from django.db.models import Q
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
import base64
from collections import defaultdict
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from django.contrib import messages




                          # Catagory side #

@login_required(login_url='base:admin_pannel')
def catagory_list(request):
    
    search_query = request.GET.get('search')

    if search_query:
        categories = Category.objects.filter(Q(category_name__icontains=search_query))
    else:
     categories = Category.objects.filter(is_active=True)

    context={

        'categories': categories
      }

    return render(request,'admin/catogry.html',context)


@login_required(login_url='base:admin_pannel')
def add_catagory(request):
    return render(request,'admin/add_catagory.html')



@login_required(login_url='base:admin_pannel')
def insert_catagoriy(request):

    if request.method == "POST":
        catagory_name = request.POST.get("catagory_name")
        description = request.POST.get("description")

        # Check if the category with the given name already exists
        if Category.objects.filter(category_name=catagory_name).exists():
            messages.error(request, "Category with this name already exists.")
            return redirect('catagorie:insert_catogory')

        # Remove leading and trailing whitespaces
        stripped_category_name = catagory_name.strip()
        stripped_description = description.strip()

        # Check if category_name contains only spaces
        if not stripped_category_name:
            messages.error(request, "Category name cannot be empty or contain only spaces.")
            return redirect('catagorie:insert_catogory')

        # Check if description contains only spaces
        if not stripped_description:
            messages.error(request, "Description cannot be empty or contain only spaces.")
            return redirect('catagorie:insert_catogory')

        # Your logic for saving the category
        new_category = Category(category_name=stripped_category_name, description=stripped_description)
        new_category.save()

        messages.success(request, "Category added successfully.")
        return redirect('catagorie:catogory_list')

    return render(request, 'admin/add_catagory.html')
       

@login_required(login_url='base:admin_pannel')
def delete_category(request, slug):
    if request.method == 'POST':
        category = Category.objects.get(slug=slug)
        category.is_active=False
        category.save()
    return redirect('catagorie:catogory_list')  # Redirect to the desired page after deletion



@login_required(login_url='base:admin_pannel')
def edit_catagory(request, category_name):
    category = get_object_or_404(Category, category_name=category_name)

    if request.method == "POST":
        new_category_name = request.POST.get("catagory_name")
        description = request.POST.get("description")

        
        stripped_new_category_name = new_category_name.strip()
        stripped_description = description.strip()

       
        if not stripped_new_category_name:
            messages.error(request, "Category name cannot be empty or contain only spaces.")
            return redirect('catagorie:edit_catagory', category_name=category_name)

        
        if not stripped_description:
            messages.error(request, "Description cannot be empty or contain only spaces.")
            return redirect('catagorie:edit_catagory', category_name=category_name)

        
        if Category.objects.exclude(pk=category.pk).filter(category_name=stripped_new_category_name).exists():
            messages.error(request, "Category with this name already exists.")
            return redirect('catagorie:edit_catagory', category_name=category_name)

        
        category.category_name = stripped_new_category_name
        category.description = stripped_description
        category.save()

        messages.success(request, "Category updated successfully.")
        return redirect('catagorie:catogory_list')

    context = {'category': category}
    return render(request, 'admin/some.html', context)   


 


                         #product side#
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
import os

def resize_image(image, output_width=1200, output_height=1080):
    # Open the image using Pillow
    original_image = Image.open(image)

    # Convert the image to RGB mode if it has an alpha channel
    if original_image.mode == 'RGBA':
        original_image = original_image.convert('RGB')

    # Resize the image
    resized_image = original_image.resize((output_width, output_height), resample=Image.BICUBIC)

    # Specify the directory for temporary files
    temp_directory = "path/to/temporary/"

    # Create the directory if it doesn't exist
    os.makedirs(temp_directory, exist_ok=True)

    # Save the resized image to a temporary file
    temp_file_path = os.path.join(temp_directory, "file.jpg")
    resized_image.save(temp_file_path)

    return temp_file_path

def add_product(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)

        if form.is_valid():
            brand_id = request.POST.get('brand')
            product_name = request.POST.get('product_name')
            category_id = request.POST.get('category')
            description = request.POST.get('description')
            price = request.POST.get('price')
            images = request.FILES.getlist('images[]')

            brand = Brand.objects.get(id=brand_id)
            category = Category.objects.get(pk=category_id)

            if not images:
                messages.error(request, 'Add images')
            else:
                product = Product(
                    brand=brand,
                    product_name=product_name,
                    description=description,
                    category=category,
                    price=price,
                    rprice=price,
                )

                # Resize and save the original product image
                resized_original_image_path = resize_image(images[0])
                product.image = SimpleUploadedFile("resized_original_image.jpg", open(resized_original_image_path, "rb").read())
                product.save()

                for i in range(1, len(images)):
                    # Resize and save additional images
                    resized_image_path = resize_image(images[i])
                    prd_image = ProductImage(product=product, image=SimpleUploadedFile(f"resized_image_{i}.jpg", open(resized_image_path, "rb").read()))
                    prd_image.save()

                    # Clean up temporary files
                    os.remove(resized_image_path)

                return redirect('catagorie:product_list')
        else:
            # Form is not valid, send error messages to the template
            messages.error(request, 'Error adding the product. Please check the form.')
    else:
        form = AddProductForm()

    context = {
        'form': form,
        'categories': categories,
        'brands': brands
    }

    return render(request, 'admin/add_product.html', context)

  

@login_required(login_url='base:admin_pannel')
def delete_product(request,product_id):

    if request.method== 'POST':
         
         product=Product.objects.get(product_id=product_id)
         print(product.product_name)
         product.is_active=False
         product.save()

    return redirect('catagorie:product_list')     
  


@login_required(login_url='base:admin_pannel')
def edit_product(request, product_id):
    categories = Category.objects.all()
    brands = Brand.objects.all()

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)

    if request.method == 'POST':
        form = EditProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('catagorie:product_list')
        else:
            messages.error(request,'Provide valid Data')
    else:
        form = EditProductForm(instance=product)

    context = {
        'form': form,
        'categories': categories,
        'brands': brands,
        'product': product,
    }

    return render(request, 'admin/edit_product.html', context)





        



@login_required(login_url='base:admin_pannel')
def produ(request):
    search_query = request.GET.get('search', '')

    # Query the products based on the search query and exclude soft-deleted products
    if search_query:
        products = Product.objects.filter(product_name__icontains=search_query, is_active=True)
    else:
        products = Product.objects.filter(is_active=True)

    context = {
        'products': products
    }

    # Provide the correct template name 'admin/product.html'
    return render(request, 'admin/products.html', context)

def pro(request):
   
   return render(request,'admin/product.html' )



                            #user management#
@login_required(login_url='base:admin_pannel')
def user_list(request):
    users = Account.objects.exclude(is_superadmin=True)
    
    context={
        'users':users
    }
    return render(request,'admin/user.html',context)


@login_required(login_url='base:admin_pannel')
def action_user(request,user_id):
    
    user = get_object_or_404(Account, id=user_id)



    # Toggle the is_blocked status of the user
    if user.is_active:
        user.is_active=False
        if request.user == user:
            logout(request)

    else:
        user.is_active=True
        
    user.save()
    return redirect('catagorie:user_list')


    


@login_required(login_url='base:admin_pannel')
def product_list(request):
    product= Product.objects.all()

    return render('admin/')





                      #varients management#


def varient_slist(request):
    varient=varients.objects.all()
    form = AddVariantForm()

    context={
        'varient':varient,
        'form':form
    }
    return render(request,'admin/varients.html',context)
    


def variant_list(request):
   

    search_query = request.GET.get('search', '')
    if search_query:
         product_varient = varients.objects.filter(
            Q(color__icontains=search_query) |
            Q(size__icontains=search_query) |
            Q(stock__icontains=search_query)
        ).distinct()
    else:
       product_varient = varients.objects.filter(is_active=True)
      # Fetch all orders from the Order model
    context = {'product_varient': product_varient}
    return render(request, 'admin/varient.html', context)


def add_variant(request, variant_id=None):
    # Check if variant_id is provided and if it exists
    if variant_id:
        variant = get_object_or_404(varients, id=variant_id)
    else:
        variant = None

    if request.method == 'POST':
        color = request.POST.get('color') 
        size = request.POST.get('size') 
        stock = request.POST.get('stock') 
        price = request.POST.get('price')
        is_active = request.POST.get('is_active') 
        product = request.POST.get('product')
        images = request.FILES.getlist('images[]')

        print(color, '', size, stock, price, is_active, product)

        products = Product.objects.get(pk=product)
        if variant:
            form = AddVariantForm(request.POST, request.FILES, instance=variant)
        else:
            form = AddVariantForm(request.POST, request.FILES)
        
        if form.is_valid():
            if not images:
                messages.error(request, 'Add images')
            else:
                exists = varients.objects.filter(product=products, color=color, size=size)
                if exists:
                    messages.error(request, 'Variation already exists')
                else:
                    varient = varients(
                        color=color,
                        stock=stock,
                        price=price,
                        size=size,
                        product=products
                    )
                    varient.image = SimpleUploadedFile(f"resized_original_image.jpg", open(resize_image(images[0]), "rb").read())
                    varient.save()

                    # Handle multiple images
                    for i in range(1, len(images)):
                        vrt_image = varientImage(varients=varient, image=SimpleUploadedFile(f"resized_image_{i}.jpg", open(resize_image(images[i]), "rb").read()))
                        vrt_image.save()

                    return redirect('catagorie:variant-list')
        else:
            messages.error(request, 'Provide valid data')
    else:
        # When editing, populate the form with existing variant data
        if variant:
            form = AddVariantForm(instance=variant)
        else:
            form = AddVariantForm()

    context = {
        'form': form,
        'variant_id': variant_id,
    }

    return render(request, 'admin/add_varients.html', context)




def edit_varients(request, variant_id):
    variant_instance = get_object_or_404(varients, id=variant_id)

    if request.method == 'POST':
        form = AddVariantForm(request.POST, instance=variant_instance)
        if form.is_valid():
            form.save()
            return redirect('catagorie:variant-list')
        else :
            messages.error(request,'Please Provide Valid Data')
    else:
        form = AddVariantForm(instance=variant_instance)

    context = {
        'form': form,
        'variant_id': variant_id,
    }

    return render(request, 'admin/edit_varients.html', context)

def delete_variant(request, variant_id):

    if not request.user.is_authenticated:
        return redirect('account:admin_login')
    
    variant = get_object_or_404(varients, id=variant_id)
    
    variant.is_active = False
    variant.save()
 
    
    return redirect('catagorie:variant-list')





                          #order management#

def order_list(request):
    if not request.user.is_authenticated:
        return redirect('account:admin_login')
    
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')  # Fetch all orders from the Order model
    context = {'orders': orders}
    return render(request, 'admin/orderlist.html', context)


def ordered_product_details(request, order_id):
    if not request.user.is_authenticated:
        return redirect('base:admin_pannel')
    
    orders = Order.objects.get(id=order_id)
    print(orders)
    order_instance = Order.objects.get(id=order_id)

# Retrieving related OrderProduct instances using the default reverse relation
    ordered_products = order_instance.orderproduct_set.all()


    print(ordered_products)
    for i in ordered_products:
        total=+(i.product_price*i.quantity)
    payments = Payment.objects.filter(order__id=order_id,user=orders.user)    

    context = {
        'total':total,
        'order': orders,
        'ordered_products': ordered_products,
        'payments':payments
    }
    return render(request, 'admin/ordered_product_details.html', context)


def update_order_status(request, order_id):
    if not request.user.is_authenticated:
        return redirect('account:admin_login')
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=int(order_id))
        status = request.POST['status']
        order.status = status
        order.save()
        if status=='Completed':
            payment=Payment.objects.get(order__id=order_id,user=order.user)
            if payment.payment_method=='Cash on Delivery':
                payment.status='Paid'
                payment.save()
        return redirect('catagorie:order_list')
    else:
        return HttpResponseBadRequest("Bad request.")
    




     #------------------------------------------Brand Management----------------------------#

import re     
def add_brand(request):
   if request.method == 'POST':
        brand_name = request.POST.get('brand_name')

        # Validate brand name using regex
        if not re.match("^[a-zA-Z0-9]+$", brand_name):
           messages.error(request,'provide proper name')
           return redirect('catagorie:add_brand')

        
        elif Brand.objects.filter(brand_name=brand_name).exists():
                 messages.error(request,'Brand name already exists')
                 return redirect('catagorie:add_brand')
        else:
            Brand.objects.create(brand_name=brand_name)
            return redirect('catagorie:brand_list')  

    
   return render(request, 'admin/add_brand.html')

   
def brand_list(request):
    brand=Brand.objects.filter(is_active=True)
    return render(request,'admin/brand_list.html',context={'brands':brand}) 

def delete_brand(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)  
    if brand:
        brand.is_active=False 
        brand.save() 
        return redirect('catagorie:brand_list')  
    

                    #coupon management#



from cart.forms import CouponForm
def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('catagorie:list_coupons')  # Redirect to the list of coupons or another page
    else:
        form = CouponForm()
    
    return render(request, 'admin/add coupons.html', {'form': form})


from cart.models import *
def list_coupons(request):
    coupons=Coupon.objects.filter(is_active=True)
    return render(request,'admin/list_coupon.html',{"coupons":coupons})

@login_required(login_url='account:admin_login')
def delete_coupon(request, id):
    if not request.user.is_authenticated:
        return redirect('base:admin_pannel')

    try:
        coupon = Coupon.objects.get(id=id)
        coupon.is_active=False
        coupon.save()
    except Coupon.DoesNotExist:
        # Handle the case where the coupon with the given ID doesn't exist
        pass

    return redirect('catagorie:list_coupons')


@login_required(login_url='account:admin_login')
def edit_coupon(request, id):
    coupon = get_object_or_404(Coupon, pk=id)
    if not request.user.is_authenticated:
        return redirect('base:admin_pannel')

    if request.method == 'POST':
        form = CouponForm(request.POST,instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('catagorie:list_coupons')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'admin/edit_coupon.html', {'form': form})

               # sales report management#



from django.db.models import Sum, F, Value, Count
from datetime import datetime, timedelta
from django.views.decorators.cache import cache_control
from django.utils import timezone



@login_required(login_url='base:admin_pannel')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def charts(request):
    if not request.user.is_authenticated:
        return redirect('base:admin_pannel')
    
    return render(request, 'admin/charts.html')


@login_required(login_url='base:admin_pannel')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reports(request):
     if not request.user.is_authenticated:
        return redirect('base:admin_pannel')
    
     return render(request, 'admin/report.html')


@login_required(login_url='account:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def filtered_sales(request):
    if not request.user.is_authenticated:
        return redirect('base:admin_pannel')
    # Get the minimum and maximum price values from the request parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    from_date = f'{start_date}+00:00'
    to_date = f'{end_date} 23:59:59+00:00'
    orders = Order.objects.filter(
        created_at__gte=from_date, created_at__lte=to_date,is_ordered=True )

    context = {
        "sales": orders,
        "start_date": start_date,
        "end_date": end_date

    }

    return render(request, 'admin/report.html', context)

from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
@login_required(login_url='base:admin_pannel')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_report(request):
    if not request.user.is_authenticated:
        return redirect('base:admin_pannel')
    
    if request.method == 'POST':
        fromd=request.POST.get('fromDate')
        tod=request.POST.get('toDate')
        from_date = request.POST.get('fromDate')
        to_date = request.POST.get('toDate')
        time_period = request.POST.get('timePeriod')
        print(time_period)

  
        if not from_date or not to_date:
            
            messages.error(request,"Please provide valid date values.")
            return redirect('catagorie:sales_report')

    
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            return HttpResponseBadRequest("Invalid date format.")

        
        if time_period == 'all':
            sales_data = Order.objects.filter(created_at__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncDate('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        elif time_period == 'daily':
            sales_data = Order.objects.filter(created_at__date__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncDate('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        elif time_period == 'weekly':
            sales_data = Order.objects.filter(created_at__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncWeek('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        elif time_period == 'monthly':
            sales_data = Order.objects.filter(created_at__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncMonth('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        elif time_period == 'yearly':
            sales_data = Order.objects.filter(created_at__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncYear('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))


        # Define the dateWise queryset for daily sales data
        dateWise = Order.objects.filter(created_at__date__range=[from_date, to_date],is_ordered=True) \
        .values('created_at__date') \
        .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        
        

        # Calculate Total Users
        total_users = Order.objects.filter(is_ordered=True).values('user').distinct().count()

        # Calculate Total Products
        total_products = OrderProduct.objects.filter(order__is_ordered=True).values('product').distinct().count()

        # Calculate Total Orders
        total_orders = Order.objects.filter(is_ordered=True).count()

        # Calculate Total Revenue
        total_revenue = Order.objects.filter(is_ordered=True).aggregate(total_revenue=Sum('order_total'))['total_revenue']
        
        context = {
            'sales_data': sales_data,
            'from_date': from_date,
            'to_date': to_date,
            'report_type': time_period,
            'total_users': total_users,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'dateWise': dateWise,
            'fromd':fromd,
            'tod':tod, 
        }

        return render(request, 'admin/sales_report.html', context)

    return render(request, 'admin/sales_report.html')




@login_required(login_url='base:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    
    if not request.user.is_authenticated:
        return redirect('base:admin_pannel')

    total_users_count = int(Account.objects.count())
    product_count = Product.objects.count()
    user_order = Order.objects.filter(is_ordered=True).count()
    # for i in monthly_order_totals:
    completed_orders = Order.objects.filter(is_ordered=True)

    monthly_totals_dict = defaultdict(float)

    # Iterate over completed orders and calculate monthly totals
    for order in completed_orders:
        order_month = order.created_at.strftime('%m-%Y')
        monthly_totals_dict[order_month] += float(order.order_total)

    print(monthly_totals_dict)
    months = list(monthly_totals_dict.keys())
    totals = list(monthly_totals_dict.values())

    variants = varients.objects.all()

    context = {
        'total_users_count': total_users_count,
        'product_count': product_count,
        'order': user_order,
        'variants': variants,
        'months': months,
        'totals': totals,


    }
    return render(request, 'admin/charts.html', context)



