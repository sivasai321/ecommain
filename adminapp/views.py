from django.shortcuts import render,redirect
from store.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import os
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import FileResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import pandas as pd
from django import template

#-----------------------------------------ADMIN VIEWS-----------------------------------------#

# Administrator Login
def adminstart(request):
    if 'sessionadmin' in request.session:
        return redirect(to='dashboard')
    if request.method == 'POST':
        username = request.POST['uname']
        password = request.POST['password']
        if len(username) == 0 or len(password) == 0:
            messages.info(request, 'Please enter all fields')
            return redirect(to='adminstart')
        
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_superuser:
            auth.login(request, user)
            request.session['sessionadmin'] = username
            return redirect('dashboard')
            
        else:
            messages.info(request, 'Invalid credentials')
            return render(request, 'adminstart.html')
    else:
        
       return render (request,"adminstart.html")

# Administrator Home Page
@login_required(login_url='adminstart')
@never_cache
def dashboard(request):  
    products=Product.objects.all()
    orders = Order.objects.all().order_by('-id')
    cart = UserCart.objects.all()
    amt=0
    for i in orders:
        amt=amt+i.amount
        print(i.amount)
    return render(request,"dashboard.html",{'orders':orders,'products':products,'carts':cart,'amt':amt })
  
# Administrator Logout  
@login_required(login_url='adminstart')
@never_cache
def logout(request):
    auth.logout(request)
    return redirect('adminstart')  

# Render all Users (Excluding Guest Users)
def users(request): 
     str=''
     user_details=User.objects.filter(is_superuser=False).exclude(email=str)
     return render(request, 'users.html',{'user_details':user_details})

# Add a Product
@login_required(login_url='adminstart')
@never_cache
def addproduct(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        small_description = request.POST['small_description']
        selling_price = request.POST['selling_price']
        category = request.POST['category']
        slug = request.POST['slug']
        tag = request.POST['tag']
        quantity = request.POST['quantity']
        print(request.FILES,"  1111")
        product_image = request.FILES['product_image'] 
        category=Category.objects.get(id=category)
        product = Product.objects.create(name=name,category=category,small_description=small_description,description=description,selling_price=selling_price,product_image=product_image,slug=slug,tag=tag,quantity=quantity)
        # product.category.add(category)
        product.save()
        return redirect('products')
    else: 
        category=Category.objects.all()
        print(category)
        return render(request, 'addproduct.html',{'categories':category})

# Add a new Category    
@login_required(login_url='adminstart')
@never_cache
def addcategory(request):
    if request.method == 'POST':
        name = request.POST['catname']
        image = request.FILES['image']
        slugname = request.POST['slugname']
        category = Category.objects.create(name=name,slug=slugname,image=image)
        category.save()
        return redirect('category')
    else:    
        return render(request, 'addcategory.html')

#Block User
@login_required(login_url='adminstart')
@never_cache
def block(request):
    id=request.GET['id']
    user=User.objects.get(id=id)
    user.is_active=False
    user.save()
    return redirect('users')

# Unblock User
def unblock(request):
    id=request.GET['id']
    user=User.objects.get(id=id)
    user.is_active=True
    user.save()
    return redirect('users')

# Render all Products
@login_required(login_url='adminstart')
@never_cache
def products(request):
    product=Product.objects.all()
    return render(request, 'products.html',{'products':product})


# Render all Categories
@login_required(login_url='adminstart')
@never_cache
def category(request):
    categories = Category.objects.all()
    return render(request, 'category.html', {'categories': categories })


# Edit Product Details
@login_required(login_url='adminstart')
@never_cache
def editproduct(request):
    id=request.GET['id']
    product = Product.objects.get(id=id)
    if request.method=='POST':
        id=request.GET['id']
        product = Product.objects.get(id=id)
        print(id)       
        name = request.POST['name']
        small_description = request.POST['small_description']
        description = request.POST['description']
        category = request.POST['category']
        slug= request.POST['slug']
        tag= request.POST['tag']
        selling_price= request.POST['selling_price']
        print(request.FILES,"  1111")
        product_image = request.FILES['product_image']
        quantity = request.POST['quantity']
        
        category=Category.objects.get(id=category)
        product = Product.objects.get(id=id)
        product.name=name
        product.description=description
        product.small_description=small_description
        product.selling_price=selling_price
        product.category=category
        product.slug=slug
        product.quantity=quantity
        product.product_image=product_image
        product.tag=tag
        product.save()
        
        return redirect('products')
    else:
        id=request.GET['id']
        product=Product.objects.get(id=id)
        category=Category.objects.all()
        return render(request, 'edit_product.html',{'product':product,'categories':category})


# Delete a Product
@login_required(login_url='adminstart')
@never_cache
def delete_product(request):
    id=request.GET['id']
    product=Product.objects.filter(id=id)
    product.delete()
    return redirect('products')

# Delete a Category
@login_required(login_url='adminstart')
@never_cache
def delete_category(request):
    id=request.GET['id']
    category=Category.objects.filter(id=id)
    category.delete()
    return redirect('category')

@login_required(login_url='adminstart')
@never_cache
def orders(request):
    order = Order.objects.all().order_by('-id')
    cart = UserCart.objects.all()
    status = ['Ordered','Shipped','Delivered','Cancelled']
    return render(request, 'orders.html',{'orders':order,'carts':cart,'status':status})

# Cancellation of order
def cancelorder(request):
    user=request.user
    id=request.GET['id']
    Order.objects.filter(id=id).update(status='Cancelled',cancel=True)
    
    
    return redirect('orders')

# Status Update of the Order
def updatestatus(request):
    id=request.GET['id']
    status=request.POST['status']
    print(id,status)
    Order.objects.filter(id=id).update(status=status)
    return redirect('orders')


# Coupons all Show
@login_required(login_url='adminstart')
def coupons(request):
    coupon=Coupon.objects.all()
    return render(request, 'coupon_management.html',{'coupons':coupon})

# Add a Coupon
def addcoupon(request):
    if request.method == 'POST':
        code = request.POST['code']
        discount = request.POST['discount']
        min_amount = request.POST['min_amount']
        start_date = request.POST['startdate']
        end_date = request.POST['enddate']
        coupon = Coupon.objects.create(code=code,discount=discount,min_amount=min_amount,start_date=start_date,end_date=end_date)
        return redirect('coupons')
    else:
        return render(request, "add_coupon.html")

#Offers
@login_required(login_url='adminstart')
@never_cache
def offers(request):
    prod_offer = Offers.objects.filter(offer_type='product')
    category_offer = Offers.objects.filter(offer_type='category')
    return render(request, 'offer_management.html',{'prod_offers':prod_offer,'category_offers':category_offer})

# Product Offer
@login_required(login_url='adminstart')
def prod_addoffer(request):
    if request.method == 'POST':
        name = request.POST['name']
        offer = request.POST['offer']
        startdate = request.POST['startdate']
        max_value = request.POST['max_value']
        print(startdate)
        enddate = request.POST['enddate']
        print( "end",enddate)
        product = request.POST['product']
        print(product)
        offer = Offers.objects.create(name=name,offer=offer,start_date=startdate,end_date=enddate,offer_type='product',product_id=product,max_value=max_value)
        offer.save()
        return redirect('offers')
    else:
        products=Product.objects.all()
        return render(request, "prod_addoffer.html",{'products':products})

# Category Offer
@login_required(login_url='adminstart')
def cate_addoffer(request):
    if request.method == 'POST':
        name = request.POST['name']
        offer = request.POST['offer']
        startdate = request.POST['startdate']
        max_value = request.POST['max_value']
        print(startdate)
        enddate = request.POST['enddate']
        print( "end",enddate)
        category = request.POST['category']
         
        offer = Offers.objects.create(name=name,offer=offer,start_date=startdate,end_date=enddate,offer_type='category',category_id=category,max_value=max_value)
        offer.save()
        return redirect('offers')
    else:
        category=Category.objects.all()
        return render(request, "cate_add_offer.html",{'category':category})

# Sales Report Page Rendering
@login_required(login_url='adminstart')
def sales(request):
    if request.method == 'POST' and 'start_date' in request.POST and 'end_date' in request.POST:
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        orders=Order.objects.filter(ordered_date__range=[start_date,end_date])
        return render(request, 'sales.html',{'orders':orders})
    orders=Order.objects.all().order_by('-id')
    return render(request, 'sales.html',{'orders':orders})

# Sale Report Admin side - PDF and Excel
@login_required(login_url='adminstart')
def report(request):
    print(request.method)
    start = request.POST['start_date']
    end = request.POST['end_date']
    print("end=",end)
    order = Order.objects.filter(ordered_date__range=[start,end])
    print(order)
    n=len(order)
    print(n)
    if n==0:
        messages.error(request, 'No Order Found')
        return redirect('sales')
    print(order)
    type = request.POST['type']
    print(type)
    if type == 'PDF':
        
        template_path = 'report.html'

        context = {'order': order}

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = 'filename="invoice.pdf"'

        template = get_template(template_path)

        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        data =[]
        for order in order:
            data.append({
                "id":order.id,
                "Customer":order.user.username,
                "Ordered date":str(order.ordered_date),
                "Amount":order.amount,
                "Payment Method":order.method,
                "Order Status":order.status,
            })
        pd.DataFrame(data).to_excel("report.xlsx")
        # response['Content-Disposition'] = 'filename="report.xlsx"'
        return FileResponse(open('report.xlsx', 'rb'), as_attachment=True, filename="report.xlsx")

# Filter the Month
@login_required(login_url='adminstart')
def monthly_sales(request):
    month = request.POST['month']
    mtz=int(month)-1
    month_list=['January','February','March','April','May','June','July','August','September','October','November','December']
    passed_month=month_list[mtz]
    orders = Order.objects.filter(ordered_date__month=month)
    if len(orders) ==0:
        return render(request, 'sales.html',{'mts':passed_month})
    return render(request, 'sales.html',{'orders':orders,'mts':passed_month})

# Filter the year
@login_required(login_url='adminstart')
def yearly_sales(request):
    year = request.POST['year']
    orders = Order.objects.filter(ordered_date__year=year)
    if len(orders) ==0:
        return render(request, 'sales.html',{'yr':year})
    return render(request, 'sales.html',{'orders':orders,'yr':year})

# Select Date Function   
def date_select(request):
    start = request.POST['start_date']
    end = request.POST['end_date']
    print("end=",end)
    order = Order.objects.filter(ordered_date__range=[start,end])
    if len(order) ==0:
        # messages.info(request, 'No Orders Found')
        return render(request, 'sales.html')
    else:
        return render(request, 'sales.html',{'orders':order})

# Yearly Report PDF/Excel
@login_required(login_url='adminstart')
def yearly(request):
    year = request.POST['year']
    type = request.POST['type']
    order = Order.objects.filter(ordered_date__year=year)
    n=len(order)
    if n==0:
        messages.error(request, 'No Order Found')
        return redirect('sales')
    if type == 'PDF':
        
        template_path = 'report.html'

        context = {'order': order}

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = 'filename="report.pdf"'

        template = get_template(template_path)

        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        data =[]
        for order in order:
            data.append({
                "id":order.id,
                "Customer":order.user.username,
                "Ordered date":str(order.ordered_date),
                "Amount":order.amount,
                "Payment Method":order.method,
                "Order Status":order.status,
            })
        pd.DataFrame(data).to_excel("report.xlsx")
        # response['Content-Disposition'] = 'filename="report.xlsx"'
        return FileResponse(open('report.xlsx', 'rb'), as_attachment=True, filename="report.xlsx")

# Monthly Report PDF/Excel
@login_required(login_url='adminstart')
def monthly(request):
    month = request.POST['month']
    type = request.POST['type']
    order = Order.objects.filter(ordered_date__month=month)
    n=len(order)
    if n==0:
        messages.error(request, 'No Order Found')
        return redirect('sales')
    if type == 'PDF':
        
        template_path = 'report.html'

        context = {'order': order}

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = 'filename="invoice.pdf"'

        template = get_template(template_path)

        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        data =[]
        for order in order:
            data.append({
                "id":order.id,
                "Customer":order.user.username,
                "Ordered date":str(order.ordered_date),
                "Amount":order.amount,
                "Payment Method":order.method,
                "Order Status":order.status,
            })
        pd.DataFrame(data).to_excel("report.xlsx")
        # response['Content-Disposition'] = 'filename="report.xlsx"
        return FileResponse(open('report.xlsx', 'rb'), as_attachment=True, filename="report.xlsx")


# Coupon Management - Block Coupon
@login_required(login_url='adminstart')
def blockcoupon(request):
    id=request.GET['id']
    coupon=Coupon.objects.filter(id=id).update(is_active=False)
    return redirect('coupons')

# Coupon Management - Unblock Coupon
@login_required(login_url='adminstart')
def unblockcoupon(request):
    id=request.GET['id']
    coupon=Coupon.objects.filter(id=id).update(is_active=True) 
    return redirect('coupons')


# Offer Management- Block
@login_required(login_url='adminstart')
def blockoffer(request):
    id=request.GET['id']
    offer=Offers.objects.filter(id=id).update(is_active=False)
    return redirect('offers')

# Offer Management- Unblock
@login_required(login_url='adminstart')
def unblockoffer(request):
    id=request.GET['id']
    offer=Offers.objects.filter(id=id).update(is_active=True)
    return redirect('offers')

# Accept Return Request
@login_required(login_url='adminstart')
def acceptrequest(request):
    id=request.GET['id']
    Order.objects.filter(id=id).update(status='Return Accepted')
    return redirect('orders')

# Reject return Request
@login_required(login_url='adminstart')
def rejectrequest(request):
    id=request.GET['id']
    Order.objects.filter(id=id).update(status='Return Rejected')
    return redirect('orders')
