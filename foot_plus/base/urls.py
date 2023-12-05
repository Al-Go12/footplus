from django.urls import path

from base import views
app_name = 'base'

urlpatterns=[
     path('',views.index,name='index'),
     path('product_detail/<int:product_id>/',views.product_detail,name='product_detail'),

     path('admin_pannel',views.admin_login,name='admin_pannel'),
     path('login',views.handlelogin,name='login'),
     path('signup',views.handlesignup,name='signup'),
     path('sp',views.sent_otp,name='sp'),
     path('resend_otp',views.resend_otp,name='resend_otp'),
     path('vp',views.veify_otp,name='vp'),
     path('logout',views.user_logout,name='logout'),
     path('alogout',views.admin_logout,name='alogout'),
     path('add_address',views.add_address,name="add_address"),
     path('base/',views.base,name='base'),
     #--------------forgetpassword------------#
     path('forgetpassword',views.sendotpforrestpass,name='forgetpassword'),
     path('sendotp',views.sent_otpforforget,name='sendotp'),
     path('verify',views.verify,name='verify'),
     path('resendotp',views.resendotps,name='resend')

     #path('db',views.db,name='db'),
    
     
     
     

]