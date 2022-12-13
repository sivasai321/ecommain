from itertools import product
from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from operator import ne
from plistlib import UID
import profile
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from store.models import Accounts
from adminapp.models import *
from .models import *
from .mixins import MessageHandler
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
import random
from django.http import JsonResponse
from guest_user.decorators import allow_guest_user
from guest_user.models import Guest
from twilio.base.exceptions import TwilioRestException,TwilioException
from twilio.rest import Client

# --------------------------VIEWS-----------------------------------#
generatedotp=0
print("gen-top",generatedotp)
# Guest User
@allow_guest_user()
@never_cache
def guest(request):
    if request.user.is_authenticated and request.user.is_superuser == False and request.user.first_name !='':
        return redirect('home')
    else:
        product = Product.objects.all()
        category = Category.objects.all()
        return render(request,'guest.html',{'product': product, 'category': category})

# User Login     
@never_cache
def loginpage(request):
    if request.user.is_authenticated and request.user.is_superuser == False and request.user.first_name !='': 
        messages.success(request,'Already Logged in')
        return redirect('home')
    if request.method == 'POST' and 'username' in request.POST and 'password' in request.POST :
        username = request.POST['username']
        password = request.POST['password']
        if len(username) == 0 or len(password) == 0:
            messages.error(request, "Please enter all fields",extra_tags='user_login')
            return redirect(to='loginpage')      
        user = auth.authenticate(request, username=username, password=password)

        if user is not None and user.is_active and user.is_superuser == False:
            auth.login(request, user)
            messages.success(request,'Logged in Successfully')
            return redirect(to='home')
        else:
            messages.info(request, "Invalid credentials", extra_tags='user_login')
            return redirect(to='loginpage')                
    else:
        return render(request, 'loginpage.html')	#context = {
			                                        # 'var1': 'John',
			                                        #}
    
    
# User sign up
def signup(request):
    print(request.POST)
    print(request.user.id)
    id = request.user.id

    if request.method == 'POST'  and 'otp' not in request.POST:
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        print("username=", username)
        print(password)
        user = User.objects.create_user(id=id,first_name=first_name, last_name=last_name,  username=username, email=email, password=password)
        user.save_base()
        user_id = User.objects.get(username=username)
        account = Accounts.objects.create(user=user_id, phone=phone)
        account.save()
        guest = Guest.objects.get(user_id=id)
        guest.delete()
        print('user created')
        return render(request,'loginpage.html')

    elif request.method == 'POST':
        phone = request.POST['phone']
        otp1 =int( request.POST['otp'])
        global generatedotp
        print(otp1)
        if generatedotp == otp1:
            return render(request, "signup.html",{ 'phone': phone})
        else:
            
            return render(request, "enterotp.html",{ 'otp': otp1, 'generatedotp':generatedotp})
  
    else:
        return render(request, 'signup.html')
      
# Generate an OTP value      
def getotp(request):
    phone = request.POST['phone']
    if len(phone) == 0 :
            messages.info(request, "Please enter all fields",extra_tags='phone_login')
            return redirect(to='login')

    otp = random.randint(100000, 999999)
    i = False
    while i == False:
       if phone.isdigit():
           i = True
       else:
            messages.info(request, "Invalid Mobile Number",extra_tags='phone_login')
            return redirect(to='loginpage')
           
    
    if not Accounts.objects.filter(phone=phone).exists():
        messages.info(request, "Phone Number Not Registered", extra_tags='phone_login' )
        return redirect('loginpage')
    else:
        num = Accounts.objects.filter(phone=phone).update(otp=otp)
        user = Accounts.objects.get(phone=phone)

    
    print(user.user)
    if user.user.is_active == False or user.user.is_superuser:
        messages.info(request, "Phone Number Not Registered", extra_tags='phone_login' )
        return redirect('loginpage')
    else:
        try:
            num = Accounts.objects.filter(phone=phone)
            message_handler = MessageHandler(phone,num[0].otp).sent_otp_on_phone()
            return redirect(f'otp/{num[0].uid}')
            print(message.sid)
        except (TwilioRestException,TwilioException):
                return redirect('error')

# Login via OTP    
@never_cache
def otplogin(request,uid):
    if request.user.is_authenticated and request.user.is_superuser == False:
        return redirect('home')
    if request.method == 'POST':
        otp=request.POST.get('otp')
        accounts = Accounts.objects.get(uid=uid)
     
        if otp == accounts.otp:
            login(request,accounts.user,backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        else:
          return redirect(f'/otp/{uid}')
    else:
     return render(request,"otp.html")    
    
    
    
def mobile_signup(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        if len(phone) == 0 :
            messages.info(request, "Please enter your Mobile Number",extra_tags='user_login')
            return redirect(to='mobile')
        
        elif Accounts.objects.filter(phone=phone).exists():
             messages.info(request, 'Mobile Number Already Registered')
             return redirect('mobile')
        else:
            global generatedotp
            otp = random.randint(100000, 999999)
            generatedotp=otp
            
            print("genotp",generatedotp)
            try:
                message_handler = MessageHandler(phone, otp).sent_otp_on_phone()
                return render(request, "enterotp.html",{ 'phone': phone})
            except (TwilioRestException,TwilioException):
                return redirect('error')
    return render(request,"enterphone.html")
    
    
          
@never_cache
def logout(request):
    auth.logout(request)
    return redirect('loginpage')          


def changepassword(request):
    id=request.GET['id']
    if request.method == 'POST':
        fname=request.POST['first_name']
        lname=request.POST['last_name']
        email=request.POST['email']
        username=request.POST['username']
        password=request.POST['password']
 
        user = User.objects.create_user(id=id,username=username, password=password, first_name=fname, last_name=lname, email=email)
        print(user.password)
        user.save_base()
        print('success')
        success=True
        return render(request,"loginpage.html",{"success":success})
    else:
         user = User.objects.filter(id=id)
         return render(request,"changepassword.html",{'user':user})    


# invoice
def invoice( request):
    id = request.GET['id']
    order = Order.objects.filter(id=id)
    user = request.user
    address=order[0].address
    cart = AdminCart.objects.filter(order_id=id)
    print(address)
    print(cart[0].product.name)
    

    template_path = 'invoice.html'

    context = {'order': order, 'address':address, 'user': user, 'cart': cart}

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'filename="invoice.pdf"'

    template = get_template(template_path)

    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return  response


# error msg
def error(request):
  return render(request,"index.html")    

