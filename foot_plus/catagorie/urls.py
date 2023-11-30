from django.urls import path,include
from catagorie import views

app_name = 'catagorie'


urlpatterns =[

    path('catogory_list',views.catagory_list,name='catogory_list'),
    path('add_catogory',views.add_catagory,name='add_catogory'),
    path('insert_catogory',views.insert_catagoriy,name='insert_catogory'),
    path('delete-category/<slug:slug>/', views.delete_category, name='delete_category'),
    path('edit_catagory/<str:category_name>/', views.edit_catagory, name='edit_catagory'),


    path('user_list',views.user_list,name='user_list'),
    path('action_user/<int:user_id>/', views.action_user, name='action_user'),

    path('add_product/', views.add_product, name='add_product'),
    path('product_list/',views.produ,name='product_list'),
    path('delete_product/<int:product_id>/',views.delete_product,name='delete_product'),
    path('edit_product/<int:product_id>/',views.edit_product,name='edit_product'),

    path('varient_slist',views.varient_slist,name='varient_slist'),
    path('variant',views.variant_list,name='variant-list'),
    path('add-variant',views.add_variant,name='add-variant'),
   path('edit_varient/<int:variant_id>/', views.edit_varients, name='edit_variant'),
    path('delete-variant/<int:variant_id>/', views.delete_variant, name='delete-variant'),

    path('order_list',views.order_list,name='order_list'),
    path('ordered_product_details/<int:order_id>', views.ordered_product_details, name='ordered_product_details'),
    path('update_order_status/<str:order_id>/', views.update_order_status, name='update_order_status'),

    path('add_coupon',views.add_coupon,name='add_coupon'),
    path('list_coupons',views.list_coupons,name='list_coupons'),
   path('delete_coupon/<int:id>/', views.delete_coupon, name="delete_coupon"),
   path('edit_coupon/<int:id>/', views.edit_coupon, name="edit_coupon"),

    path('add_brand/',views.add_brand,name='add_brand'),
    path('brand_list/',views.brand_list,name='brand_list'),
    path('delete-brand/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    

    path('dashboard/', views.dashboard, name='dashboard'),
    path('chart/',views.charts,name='charts'),
    path('reports/',views.reports,name='reports'),
    path('sales-report/', views.sales_report, name='sales_report'),

    path('filtered_sales/', views.filtered_sales, name='filtered_sales'),
]


