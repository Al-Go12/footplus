from . import views
from django.urls import path
app_name='user'

urlpatterns = [
     path('user_dashboard/',views.user_orders, name='user_dashboard'),
     path('order_details/<int:order_id>/',views.order_details,name='order_details'),
     path('edit_profile/',views.edit_profile,name='edit_profile'),
     path('profile/',views.profile,name='profile'),
     path('user_address/',views.user_addres,name='user_address'),
     path('add_address/',views.add_address,name='add_address'),
     path('add_adresss/',views.add_addresss,name='add_addresss'),
     path('edit_address/<int:id>/',views.edit_address,name='edit_address'),
     path('delete_address/<int:id>/',views.delete_address,name='delete_address'),
     path('cancel_order_product/<int:order_id>/',views.cancel_order_product,name='cancel_order_product'),
     path('change_password',views.change_password,name='change_password')

           
]