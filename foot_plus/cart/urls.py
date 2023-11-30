from . import views
from django.urls import path


app_name='cart'

urlpatterns = [
    path('shoping_cart/', views.cart, name='shopping_cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    

    path('ajax/update/cart/', views.newcart_update, name='newcart_update'),
    path('ajax/remove/cart/', views.remove_cart_item_fully, name='remove_cart_item_fully'),


    path('checkout',views.checkout,name="checkout"),
    path('add_address',views.add_address,name="add_address"),
    path('place_order',views.place_order,name="place_order"),
    path('payment',views.paytment,name="payment"),
    path('order_success/<int:id>/', views.order_success, name='order_success'),
    path('confirm_razorpay_payment/<str:order_number>/', views.confirm_razorpay_payment, name='confirm_razorpay_payment'),
    


    path('apply_coupon',views.apply_coupon,name='apply_coupon'),
     path('remove_coupon/',views.remove_coupon, name='remove_coupon'),

]
