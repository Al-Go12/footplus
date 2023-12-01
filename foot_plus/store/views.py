from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from store.models import *
from userside.models import *
from catagorie.models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
import os





#----------------------------------------Banner------------------------#
def resize_image(image, output_width=1200, output_height=380):
    original_image = Image.open(image)
    if original_image.mode == 'RGBA':
        original_image = original_image.convert('RGB')

    resized_image = original_image.resize((output_width, output_height), resample=Image.BICUBIC)

    temp_directory = "path/to/temporary/"
    os.makedirs(temp_directory, exist_ok=True)

    temp_file_path = os.path.join(temp_directory, "resized_image.jpg")
    resized_image.save(temp_file_path)

    return temp_file_path



 

def add_banners(request):
 if request.method == 'POST':
    banner_name = request.POST.get('banner_name')
    images = request.FILES.getlist('images[]')

    if not banner_name or not images:
        return JsonResponse({'success': False, 'message': 'Provide Proper banner name and images'})
        
    else:
            

            banner = Banner.objects.create(banner_name=banner_name)
            for image in images:
                resized_image_path = resize_image(image)
                banner_image = BannerImage(banner=banner, images=SimpleUploadedFile("resized_image.jpg", open(resized_image_path, "rb").read()))
                banner_image.save()

                # Clean up temporary files
                os.remove(resized_image_path)

            JsonResponse({'success': True, 'message': 'Banner added successfully'})
            return redirect('store:display')
  
        


 return render(request, 'admin/add_banner.html')


def display(request):
    banners = Banner.objects.all()
    return render(request, 'admin/list_banner.html', {'banners': banners})


from django.http import JsonResponse

def toggle_set(request, banner_id):
  if request.method=='POST':  
    print('hai')
    banner = get_object_or_404(Banner, id=banner_id)
    print(banner)
    banner_name = banner.banner_name
    banner.set = not banner.set
    banner.save()


    Banner.objects.exclude(id=banner_id).update(set=False)

    message = f'{banner_name} is set as default Banner' 
    messages.success(request, message)

    return redirect('store:display')
  


def delete_banner(request,banner_id):
    banner=Banner.objects.get(pk=banner_id)
    if banner.set==True:
       messages.error(request,'This banner is set as default banner,Set another one')
    else:
        banner.delete()   
    return redirect('store:display')


#--------------------------------------- wish List---------------------------#


@login_required(login_url='base:login')
def add_wishList(request,product_id):
    product = get_object_or_404(Product, pk=product_id)
    print(product)

    try:
        vs = WishList.objects.get(user=request.user, product=product)
    except WishList.DoesNotExist:
        vs = None

    if vs is not None:
        messages.error(request, 'Product Already in wishlist')
    else:
        wishlist = WishList.objects.create(user=request.user, product=product)
        messages.success(request, 'Added Product to wishlist')
        
    return redirect('base:index')

@login_required(login_url='base:login')
def wishlist(request):
    wishlist=WishList.objects.filter(user=request.user)
    print(wishlist)
    context={
        'wishlist':wishlist
    }
    return render(request,'USER/wishlist.html',context)


@login_required(login_url='base:login')
def remove_from_wishlist(request, product_id):
    print(product_id,'hai')
    if request.method == 'POST' or request.method == 'DELETE':
        product = get_object_or_404(Product, pk=product_id)
        wishlist_item = get_object_or_404(WishList, user=request.user, product=product)

        # Assuming you have a method to remove the item from the wishlist
        wishlist_item.delete()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})