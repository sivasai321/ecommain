from unicodedata import name
from django.urls import path
from . import views
#admin views

urlpatterns =[
    
    path("",views.adminstart,name="adminstart"),
    path("dashboard",views.dashboard,name="dashboard"),
    path('adminlogout',views.logout, name='adminlogout'),
    path("users",views.users,name="users"),
    path("products",views.products,name="products"),
    path("category",views.category,name="category"),
    path('addproduct',views.addproduct,name='addproduct'),
    path('addcategory',views.addcategory,name='addcategory'),
    path('delete_category',views.delete_category,name='delete_category'),
    path('editproduct',views.editproduct,name='editproduct'),
    path('deleteproduct',views.delete_product,name='delete_product'),
    path('block',views.block,name='block'),
    path('unblock',views.unblock,name='unblock'),
    path('adminlogout',views.logout, name='adminlogout'),
    path("orders",views.orders,name="orders"),
    path('cancelorder',views.cancelorder, name='cancelorder'),
    path('updatestatus',views.updatestatus, name='updatestatus'),
    path('coupons',views.coupons, name='coupons'),
    path('addcoupon',views.addcoupon, name='addcoupon'),
    path("offers",views.offers,name="offers"),
    path('prod_addoffer',views.prod_addoffer, name='prodoffer'),
    path('cate_addoffer',views.cate_addoffer, name='cateoffer'),
    path('sales',views.sales, name='sales'),
     path('date_select',views.date_select, name='date_select'),
    path('monthly',views.monthly, name='monthly'),
    path('monthly_sales',views.monthly_sales, name='monthly_sales'),
    path('yearly_sales',views.yearly_sales, name='yearly_sales'),
    path('yearly',views.yearly, name='yearly'),
    path('report',views.report, name='report'),
    path('blockcoupon',views.blockcoupon, name='blockcoupon'),
    path('unblockcoupon',views.unblockcoupon, name='unblockcoupon'),
    path('blockoffer',views.blockoffer, name='blockoffer'),
    path('unblockoffer',views.unblockoffer, name='unblockoffer'),
    path('acceptrequest',views.acceptrequest, name='acceptrequest'),
    path('rejectrequest',views.rejectrequest, name='rejectrequest'),
    
 ]