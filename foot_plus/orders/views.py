from django.shortcuts import render,HttpResponse,redirect
from base.models import*
from cart.models import *
from userside.models import *
from orders.models import *
from cart.urls import *
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.

def wallet_details(request):
    
    try:
       wallets=wallet.objects.get(user=request.user)
    except wallet.DoesNotExist:
        wallets=wallet.objects.create(user=request.user,wallet_amount=0)
    wallet_amount=wallets.wallet_amount
    user=request.user

    context={
        'wallet_amount':wallet_amount,
        'user':user
        
    } 
    return render(request,'user/wallet.html',context)

def pay_wallet_details(request, order_number, order_total):
    grand_total = order_total
    order_number = order_number

    if request.method == 'POST':
        action = request.POST.get('action')
        grand_total = request.POST.get('grand_total')
        order_number = request.POST.get('order_number')
        print(order_number)

        try:
            wallets = wallet.objects.get(user=request.user)
        except wallet.DoesNotExist:
            wallets = wallet.objects.create(user=request.user, wallet_amount=0)
            wallets.save()

        if wallets.wallet_amount <= float(grand_total):
            print("error")
            messages.error(request, "Wallet out of balance")
            try:
                order = Order.objects.get(order_number=order_number, is_ordered=False)
            except Order.DoesNotExist:
                return HttpResponse("Order not found")

            cart_items = CartItem.objects.filter(user=request.user)
            selected_address_id = request.session.get('selected_address_id')

            if selected_address_id is not None:
                selected_address = Address.objects.get(pk=selected_address_id)
                del request.session['selected_address_id']
            else:
                selected_address_id = request.POST.get('selected_address')
                if selected_address_id is None:
                    messages.error(request, 'Choose an address or add address')
                    return redirect('cart:checkout')
                else:
                    selected_address = Address.objects.get(pk=selected_address_id)
                    coupon_discount = request.session.get('coupon_discount', 0)
                    final_total = 0
                    quantity = 0
                    total = 0
                    tax = 0
                    for cart_item in cart_items:
                        total += (cart_item.product.price * cart_item.quantity)
                        quantity += cart_item.quantity
                    tax = (2 * total) / 100
                
                    print(coupon_discount,'fg')
                    final_total = (total + tax) - coupon_discount
                    context = {
                        'order': order,
                        'cart_items': cart_items,
                        'total': total,
                        'tax': tax,
                        'coupon_discount':coupon_discount,
                        'final_total': final_total,
                        'selected_address': selected_address,
                    }
                    return render(request, 'user/payment.html', context)

        else:
                print('action is done')
                try:
                    order = Order.objects.get(order_number=order_number, is_ordered=False)
                except Order.DoesNotExist:
                    return HttpResponse("Order not found")

                print('action is done')
                payment = Payment.objects.create(
                    user=request.user,
                    payment_method="Wallet Payment",
                    amount_paid=grand_total,
                    status="Paid",)

                order.payment = payment
                order.save()
                
                
                cp = request.session.get('coupon_code')
                if cp is not None:
                    ns = Coupon.objects.get(code=cp)
                    reddemcoupon = RedeemedCoupon.objects.filter(user=request.user, coupon=ns, is_redeemed=False)
                    reddemcoupon.is_redeemed = True
                    reddemcoupon.update(is_redeemed=True)
                    del request.session['coupon_code']
                    
                   

                cart_items = CartItem.objects.filter(user=request.user, is_active=True)

                # Access the related variants instance
                # Update the stock for the variants
                for item in cart_items:
                    orderproduct = OrderProduct()
                    item.variations.stock -= item.quantity
                    item.variations.save()
                    orderproduct.order = order
                    orderproduct.payment = payment
                    orderproduct.user = request.user
                    orderproduct.product = item.product
                    orderproduct.quantity = item.quantity
                    orderproduct.product_price = item.variations.price
                    orderproduct.ordered = True
                    orderproduct.size = item.variations.size
                    orderproduct.color = item.variations.color
                    orderproduct.save()

                # Update the product's quantity or perform any other necessary updates
                cart_items.delete()    
                wallets.wallet_amount -= float(grand_total)
                wallets.save()
                return redirect("cart:order_success", id=order.id)
            



def return_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order_method=order.payment.payment_method
    if  order_method!='Cash on Delivery'and order.status == 'Completed':
        user_profile = request.user
        wallets,create = wallet.objects.get_or_create(user=user_profile)

        # Credit the purchased amount back to the wallet
        wallets.wallet_amount += order.order_total
        wallets.wallet_amount = round(wallets.wallet_amount, 2)
        wallets.save()
       
        # Update the order status to 'Returned'
        order.status = 'Rejected'
        order.save()
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            product = order_product.product.product_id
            product_variants = varients.objects.filter(product_id=product)
                        
            for variant in product_variants:
             variant.stock += order_product.quantity
             variant.save()
        messages.warning(request, 'return request has been send. amount sucessfully returned to your wallet')

    elif order_method=='Cash on Delivery' and order.status == 'Completed':
        order.status = 'Rejected'
        order.save()
        messages.warning(request, 'return request has been send.')

    elif order_method=='Cash on Delivery' and order.status != 'Completed' :
        order.status = 'Cancelled'
        order.save()
        messages.warning(request, 'return request has been send.')
    else:
        user_profile = request.user
        wallets,create = wallet.objects.get_or_create(user=user_profile)

        # Credit the purchased amount back to the wallet
        wallets.wallet_amount += order.order_total
        wallets.wallet_amount = round(wallets.wallet_amount, 2)
        wallets.save()
       
        # Update the order status to 'Returned'
        order.status = 'Cancelled'
        order.save()
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            product = order_product.product.product_id
            product_variants = varients.objects.filter(product_id=product)
                        
            for variant in product_variants:
             variant.stock += order_product.quantity
             variant.save()
        messages.warning(request, 'cancel request has been send. amount sucessfully returned to your wallet')
    return redirect('user:user_dashboard') 
    





def product_list(request):
    # Retrieve all products initially
  products = Product.objects.filter(
    varients__isnull=False,
    is_active=True,
    brand__is_active=True, 
    category__is_active=True).distinct()   
  if request.method=="GET":
    products = Product.objects.filter(varients__isnull=False,is_active=True,brand__is_active=True,category__is_active=True).distinct()   
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    print(brand)
    min_price = request.GET.get('min_price')
    if not min_price:
       min_price =0  
    max_price= request.GET.get('max_price')
    
    sort_by = request.GET.get('sort_by')
    print(sort_by)
    if category:
     selected_category= Category.objects.get(pk=category)
    else:
        selected_category='All'
    if brand:
     selected_brand =Brand.objects.get(pk=brand)
    else:
        selected_brand='All'
    if category and brand:
        products = products.filter(category=category, brand=brand)
    elif category:
        products = products.filter(category=category)
        
    elif brand:
        products = products.filter(brand=brand)
    
    if max_price and min_price:
        print(min_price, max_price)
        products = products.filter(price__gte=min_price, price__lte=max_price)
        print(products)

    # Apply sorting
    if sort_by == 'highToLow':
        products = products.order_by('-price')
    elif sort_by == 'lowToHigh':
        products = products.order_by('price')

    
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    context = {
        'products': products,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
        'selected_sort_by': sort_by,
        'categories': categories,
        'brands': brands,
        'min_price':min_price,
        'max_price':max_price,
    }

    return render(request, 'user/product_filter.html', context)
    
  else:
      categories = Category.objects.all()
      brands = Brand.objects.all()
      context = {
       'products': products,
       'categories': categories,
      'brands': brands,
                           }

      return render(request, 'user/product_filter.html', context)
      
        

def search(request):
    products = Product.objects.filter(varients__isnull=False,is_active=True,brand__is_active=True,category__is_active=True).distinct()   

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = products.filter(product_name__icontains=keyword, varients__isnull=False).distinct()

    context = {
        'products': products,
    }

    return render(request, 'user/searchproduct.html', context)
                  
            







