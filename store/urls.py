from django.contrib import admin
from django.urls import path,include
from . import views 
from . import userview
urlpatterns = [ 
    path('',userview.guest,name='guest'),
    path('home',views.home,name='home'),
    path('collections',views.collections,name='collections'),
    path('collectionsview',views.collectionsview,name='collectionsview'),
    path('productview',views.productview,name="productview"),
    path('loginpage',userview.loginpage,name='loginpage'),
    path('signup',userview.signup,name='signup'),
    path("mobile",userview.mobile_signup,name="mobile"),
    path('otp/<uid>',userview.otplogin, name='otplogin'),
    path('getotp',userview.getotp, name='getotp'),
    path('addtocart',views.addtocart, name='addtocart'),
    path("mycart",views.addtomycart,name="mycart"),
    path('cart',views.viewcart, name='cart'),
    path('logout',userview.logout, name='logout'),
    path('up',views.up,name="up"),
    path('down',views.down,name="down"),
    path('removecart',views.removecart,name='removecart'),
    path('checkout',views.checkout,name='checkout'),
    path('addaddress',views.addaddress,name='addaddress'),
    path('payment',views.payment,name='payment'),
    path('myorder',views.myorder,name='myorder'),
    path('cancelorder',views.cancelorder,name='cancelorder'),
    path('profile',views.myprofile,name='profile'),
    path('cod',views.cod,name='cod'),
    path('razorpay',views.razorpay,name='razorpay'),
    path('changepassword',userview.changepassword,name='changepassword'),
    path('invoice',userview.invoice,name='invoice'),
    path('error',userview.error,name='error'),
 
]
