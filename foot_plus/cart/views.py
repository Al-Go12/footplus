from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404,HttpResponse
from django.http import JsonResponse, HttpResponseBadRequest
from catagorie.models import *
from .models import *
from orders.models import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse
import datetime
from orders.forms import OrderForm
from django.db import transaction
#import razorpay
#client = razorpay.Client(auth=("rzp_test_dVGw4C9qQAugCR", "YOUR_SECRET"))

#data = { "amount": 500, "currency": "INR", "receipt": "order_rcptid_11" }
#payment = client.order.create(data=data)
# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
     cart = request.session.create()

    return cart


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.variations.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass 

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'USER/cart.html', context)


def add_cart(request, product_id):
   
   
   color = request.GET.get('color')
   size = request.GET.get('size')
   print(color,size)
   
   if not color:
       messages.error(request,'chose color')
   
       return HttpResponseRedirect(reverse('base:product_detail', args=(product_id,)))
       
   if not  size.isdigit() : 
        messages.error(request,'chose Size')
   
        return HttpResponseRedirect(reverse('base:product_detail', args=(product_id,)))
    
   else: 

    product = Product.objects.get(product_id=product_id)

    try:
        variant = varients.objects.get(product=product, color=color, size=size)
    except varients.DoesNotExist:
        messages.warning(request, 'Variation not available, please select another variation')
        return HttpResponseRedirect(reverse('base:product_detail', args=(product_id,)))

    if variant.stock >= 1:
        if request.user.is_authenticated:
            try:
                is_cart_item_exists = CartItem.objects.filter(
                    user=request.user, product=product, variations=variant).exists()
            except CartItem.DoesNotExist:
                is_cart_item_exists = False

            if is_cart_item_exists:
                to_cart = CartItem.objects.get(user=request.user, product=product, variations=variant)
                variation = to_cart.variations
                if to_cart.quantity < variation.stock:
                    to_cart.quantity += 1
                    to_cart.save()
                else:
                    messages.success(request, "Product out of stock")
            else:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                except Cart.MultipleObjectsReturned:
                    # If multiple records exist, choose the first one
                    cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(cart_id=_cart_id(request))
                to_cart = CartItem.objects.create(
                    user=request.user,
                    product=product,
                    variations=variant,
                    quantity=1,
                    is_active=True,
                    cart=cart  # Associate the CartItem with the Cart
                )
            return redirect('cart:shopping_cart')
        else:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.MultipleObjectsReturned:
                # If multiple records exist, choose the first one
                cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(request))
            is_cart_item_exists = CartItem.objects.filter(cart=cart, product=product, variations=variant).exists()
            if is_cart_item_exists:
                to_cart = CartItem.objects.get(cart=cart, product=product, variations=variant)
                to_cart.quantity += 1
            else:
                to_cart = CartItem(cart=cart, product=product, variations=variant, quantity=1)
            to_cart.save()
            return redirect('cart:shopping_cart')
    else:
        messages.warning(request, 'This item is out of stock.')
        return redirect('base:product_detail', product_id)

    messages.warning(request, 'Variant not found.')  # Add an error message for debugging
    return redirect('base:product_detail', product_id)




def remove_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, product_id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            variant = cart_item.variations
            variant.stock += 1
            cart_item.quantity -= 1

            variant.save()
            cart_item.save()    
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart:shopping_cart')



def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, product_id=product_id)

    try:
        if request.user.is_authenticated:
            # If the user is authenticated, remove the cart item associated with the user
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            # If the user is not authenticated, remove the cart item associated with the session cart
            cart_item = CartItem.objects.get(product=product, cart__cart_id=_cart_id(request), id=cart_item_id)
        
        # Delete the cart item
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass  # Handle the case where the cart item doesn't exist

    # Redirect back to the shopping cart page
    return redirect('cart:shopping_cart')





 
def newcart_update(request):
    new_quantity = 0
    total = 0
    tax = 0
    grand_total = 0
    quantity=0
    counter=0

    if request.method == 'POST' and request.user.is_authenticated:
        prod_id = int(request.POST.get('product_id'))
        cart_item_id = int(request.POST.get('cart_id'))
        qty=int(request.POST.get('qty'))
        counter=int(request.POST.get('counter'))
        print(qty)
        product = get_object_or_404(Product, product_id=prod_id)

        try:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            cart_items = CartItem.objects.filter(user=request.user)
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cart item not found'})
        
        if cart_item.variations:
            print('hjsgfgfhghjfg')
            print(cart_item.variations)
            variation = cart_item.variations  # Access the variation associated with the cart item
            if cart_item.quantity < variation.stock:
                cart_item.quantity += 1
                cart_item.save()
               
                sub_total=cart_item.quantity * variation.price
                new_quantity = cart_item.quantity
            else:
                message = "out of stock"
                return JsonResponse({'status': 'error', 'message': message})      
        for cart_item in cart_items:
            total += (cart_item.variations.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
        print(new_quantity,total,tax,grand_total,sub_total)       
        
        

    if new_quantity ==0:
        message = "out of stock"
        return JsonResponse({'status': 'error', 'message': message})
    else:
        return JsonResponse({
            'status': "success",
            'new_quantity': new_quantity,
            "total": total,
            "tax": tax,
            'counter':counter,
            "grand_total": grand_total,
            "sub_total":sub_total,
            
        })






def remove_cart_item_fully(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            counter = int(request.POST.get('counter'))
            product_id = int(request.POST.get('product_id'))
            cart_item_id = int(request.POST.get('cart_id'))

            # Get the product and cart item
            product = get_object_or_404(Product, product_id=product_id)
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            cart_items = CartItem.objects.filter(user=request.user)

            # Check if the cart item exists and belongs to the logged-in user
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                sub_total = cart_item.quantity * cart_item.variations.price

                total = 0
                quantity = 0

                for cart_item in cart_items:
                    total += (cart_item.variations.price * cart_item.quantity)
                    quantity += cart_item.quantity

                tax = (2 * total) / 100
                grand_total = total + tax
                current_quantity = cart_item.quantity

                return JsonResponse({
                    'status': 'success',
                    'tax': tax,
                    'total': total,
                    'grand_total': grand_total,
                    'counter': counter,
                    'new_quantity': current_quantity,
                    'sub_total': sub_total,  # Updated quantity
                })
            else:
                cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
                cart_item.delete()
                message = "the cart item has bee deleted"
                return JsonResponse({'status': 'error', 'message': message}) 

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return HttpResponseBadRequest('Invalid request')




def checkout(request,total=0, quantity=0, cart_items=None):
        
    if not request.user.is_authenticated:
        return redirect('base:index')
    if 'coupon_discount' in request.session:
                del request.session['coupon_discount']
    try:
        tax = 0
        grand_total = 0
        coupon_discount = 0

        if request.user.is_authenticated:
           cart_items = CartItem.objects.filter(user=request.user, is_active=True)
           addresses = Address.objects.filter(user=request.user,is_active=True)
           coupons = Coupon.objects.filter(is_active=True)
           

           coupons = [coupon for coupon in coupons if coupon.validate_usage_count(request.user)]
           print(coupons)

          
        else:
            addresses = []


        for cart_item in cart_items:
            total += (cart_item.variations.price * cart_item.quantity)
            quantity += cart_item.quantity

            try:
                variant = cart_item.variations
                if variant.stock <= 0:
                    print("Not enough stock!")
            except ObjectDoesNotExist:
                pass

        tax = (2 * total) / 100


        grand_total = total + tax  

        
    except ObjectDoesNotExist:
        pass

    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'addresses':addresses,
        'tax': tax,
        'grand_total': grand_total,
        'coupons'  : coupons,
      
        
    }


    return render(request,'USER/checkout.html',context)




def add_address(request):
    return render(request,'USER/add address.html')



def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('base:index')
    
    final_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.variations.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    
    coupon_discount = request.session.get('coupon_discount', 0)
    final_total = (total + tax)-coupon_discount

    
    
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            
            
            
            
            
            
            data = form.save(commit=False)
            data.user = current_user
            data.discount=coupon_discount
            data.order_total = final_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            
        
            selected_address_id = request.session.get('selected_address_id')
            
            if selected_address_id is not None:
                selected_address = Address.objects.get(pk=selected_address_id)
                data.selected_address = selected_address
                del request.session['selected_address_id']
            else:
                selected_address_id = request.POST.get('selected_address')
                if selected_address_id is None:
                    messages.error(request,'chose an address or add address') 
                    return redirect('cart:checkout')
                else:

                 selected_address = Address.objects.get(pk=selected_address_id)
                
                 data.selected_address = selected_address

            
            data.save()
            
                
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            
              #Remove the coupon_discount from the session
            
            if 'coupon_discount' in request.session:
                
                cp=request.session.get('coupon_code')
                ns=Coupon.objects.get(code=cp)

                reddemcoupon= RedeemedCoupon(
                    coupon=ns,
                    user=request.user,
                    redeemed_date=current_date,
                    is_redeemed=False,
                )  
                 
                reddemcoupon.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            selected_address = order.selected_address
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'coupon_discount':coupon_discount,
                'final_total' : final_total,
                'selected_address': selected_address,
            }
            return render(request, 'USER/payment.html', context)
        else:
            return redirect('cart:checkout')
        


from datetime import date


            


def apply_coupon(request):
   
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        grand_total_str = request.POST.get('grand_total', '0')  
        grand_total = float(grand_total_str)

        try:
            coupon = Coupon.objects.get(code=coupon_code)
            min=coupon.minimum_purchase_value
            max=coupon.maximum_purchase_value
            minimum=float(min)
            maximum=float(max)
           
             
           
        except Coupon.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Coupon not found'})

        if not coupon.is_active:
            return JsonResponse({'status': 'error', 'message': 'Coupon is not active'})
        if grand_total < minimum or grand_total > maximum:
                print(f'grand_total: {grand_total}, minimum: {minimum}, maximum: {maximum}')  # Print values for debugging
                return JsonResponse({'status': 'error', 'message': 'Not in between price range'})
 

       
        
       

        if coupon.expiration_date < date.today():
            return JsonResponse({'status': 'error', 'message': 'Coupon has expired'})
        

       
        coupon_discount = (coupon.discount / 100) * grand_total
        final_total = grand_total - int(coupon_discount)

        # Store the coupon_discount in the session
        request.session['coupon_discount'] = int(coupon_discount)
        request.session['coupon_code'] = coupon_code

        response_data = {
            'status': 'success',
            'coupon_discount': coupon_discount,
            'final_total': final_total,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
@csrf_exempt
def remove_coupon(request):
    if 'coupon_discount' in request.session:
        # Remove coupon data from the session
        del request.session['coupon_discount']
        del request.session['coupon_code']
        grand_total = float(request.POST.get('grand_total', '0'))
        response_data = {
            'status': 'success',
            'coupon_discount': 0,
            'final_total':  grand_total, 
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'No coupon applied'})

def paytment(request):
   if request.method == 'POST':
        print(request.POST)
        action = request.POST.get('action')
        selected_address_id = request.POST.get('selected_address')
        grand_total = request.POST.get('grand_total')
        print(grand_total)
        order_number = request.POST.get('order_number')
        print(order_number)  
        
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=False)
        except Order.DoesNotExist:
            
            return HttpResponse("Order not found")

        if action == "Cash on Delivery":
            print('action is done')
            payment = Payment.objects.create(
                user=request.user,
                payment_method="Cash on Delivery",  
                amount_paid=grand_total,  
                status="Pending",  
            )

            
            order.payment = payment
            order.save()

            cp=request.session.get('coupon_code')
            if cp is not None:
             ns=Coupon.objects.get(code=cp)
             reddemcoupon= RedeemedCoupon.objects.filter(user=request.user,coupon=ns,is_redeemed=False)
             reddemcoupon.is_redeemed=True
             reddemcoupon.update(is_redeemed=True)
             del request.session['coupon_code']
            
             
             

            
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            
      # Access the related varients instance
     # Update the stock for the varients
        
            for item in cart_items:
                orderproduct = OrderProduct()
                item.variations.stock-=item.quantity
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
           
            

            



        
            
            
            return redirect("cart:order_success", id=order.id) 
        else:
            return render(request, 'USER/payment.html')
        


#2023110988
@transaction.atomic
def confirm_razorpay_payment(request, order_number):

    
    current_user = request.user
    try:
        order = Order.objects.get(order_number=order_number, user=current_user, is_ordered=False)
    except Order.DoesNotExist:
        return HttpResponse("Order not found")
        
    
    total_amount = order.order_total 


    payment = Payment.objects.create(
        user=current_user,
        payment_method="Razorpay",
        status="Paid",
        amount_paid=total_amount,
    )
    

    order.payment = payment
    order.save() 
    cp=request.session.get('coupon_code')
    if cp is not None:
     ns=Coupon.objects.get(code=cp)
     reddemcoupon= RedeemedCoupon.objects.filter(user=request.user,coupon=ns,is_redeemed=False)
     reddemcoupon.is_redeemed=True
     reddemcoupon.update(is_redeemed=True)
     del request.session['coupon_code']
             
             

            
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            
      # Access the related varients instance
     # Update the stock for the varients
    for item in cart_items:
            orderproduct = OrderProduct()
            item.variations.stock-=item.quantity
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
           
    return redirect("cart:order_success", id=order.id)        



def order_success(request, id):
     try:
        order = get_object_or_404(Order, id=id)
        order_products = OrderProduct.objects.filter(order=order)
        
        order.status = 'New'
        #order.payment.status = "Completed"
        order.is_ordered=True
        order.save()
        
        print(f"Order {order.order_number} status updated to 'Completed'")
     except Exception as e:
        # Log any exceptions that occur during the update
        print(f"Error updating order status: {str(e)}")
     context = {
        'order': order,
        'order_products': order_products,
     }
     return render(request, 'USER/order_sucess.html', context)