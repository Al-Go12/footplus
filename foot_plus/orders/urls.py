from .import views
from django.urls import path



app_name='orders'

urlpatterns = [
              path('wallet',views.wallet_details,name="wallet"),
              path('pay_wallet_details/<str:order_number>/<str:order_total>/', views.pay_wallet_details, name="pay_wallet_details"),
              path('return_order/<int:order_id>/', views.return_order, name='return_order'),
              path('product_list',views.product_list,name='product_list'),


              path('search/', views.search, name='search'),
]