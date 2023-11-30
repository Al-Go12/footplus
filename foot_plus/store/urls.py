from django.urls import path
from store import views 

app_name = 'store'

urlpatterns = [
    path('add_banner/', views.add_banners, name='add_banner'),
    path('display/',views.display,name='display'),
    path('toggle_set/<int:banner_id>/',views.toggle_set,name='toggle_set'),
    path('delete_banner/<int:banner_id>',views.delete_banner,name='delete_banner'),
    path('add_wishlist/<int:product_id>',views.add_wishList,name='add_wishlist'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('remove_from_wishlist/<int:product_id>/',views.remove_from_wishlist, name='remove_from_wishlist'),
]