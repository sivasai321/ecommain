from itertools import product
from django.http import JsonResponse
from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from guest_user.decorators import allow_guest_user


# Create your views here.
generatedotp=0
offerprice=0

@login_required(login_url='loginpage')
@never_cache
def home(request):                                        # To render the home page
  category=Category.objects.filter(status=1)
  products=Product.objects.filter(status=1)

  if request.user.is_authenticated and request.user.is_superuser == False:
        print(request.user.is_authenticated)
        user = request.user
        print('user=', user)
        return render(request,'home.html', {'user': user, 'products': products, 'category': category})

  else:
        return render(request, 'guest.html', {'products': products, 'category': category})

                                                  

def collections(request):                                  # To show all the Categories
  category=Category.objects.filter(status=1) 
  context={'category':category}
  return render(request,'collections.html',context)


def collectionsview(request):                         # products_index.html -- to show all products inside a category
  id=request.GET['id']
  offers= Offers.objects.all
  catall=Category.objects.all
  if(Category.objects.filter(id=id,status=1)):
   products=Product.objects.filter(category__id=id)
   category=Category.objects.filter(id=id).first()
   context={'products':products,'category':category, 'offers':offers,'catall':catall}
   return render(request,"products_index.html",context)
  
  else:
    messages.warning(request,"No such categories found")
    return redirect('collections')
  
  
  
  
def productview(request):              # to detail individual products

    id = request.GET['id']
    if Product.objects.filter(id=id).exists():     
        product = Product.objects.get(id=id)
        prdct = Product.objects.filter(id=id)
        offer_product=''
        offer_category=''
        categories=Category.objects.get(product=id)
   
        if Offers.objects.filter(product_id=id).exists():        #product offer
            offer_product=Offers.objects.get(product_id=id)
            print("Product Offer",offer_product.offer)
        if Offers.objects.filter(category=categories.id).exists():            #Category offer
            offer_category = Offers.objects.get(category=categories.id)
            print("Category Offer",offer_category.offer)
            
        images = Images.objects.filter(product=prdct[0].id)
        print(images,"image")
        offers = Offers.objects.all()
        for offer in offers:
            print(offer.product)
            print(prdct[0])
            if offer.product == prdct[0]:
                for ofr in offers:
                
                    if ofr.category == product.category:
                        print("ofr=",ofr.name)
                        if ofr.offer<offer.offer:
                            print("offer",offer.offer)
                                
                            return render(request, 'viewproducts.html',{'product': product,'images': images,  'offer': offer, 'offer_category':offer_category, 'offer_product': offer_product})
                        else:
                            return render(request, 'viewproducts.html',{'product': product,'images': images,  'offer':ofr,  'offer_category':offer_category, 'offer_product': offer_product})
                        
            else: 
                for ofr in offers:
                    if ofr.category == product.category:
                        print("elseoffer=",ofr.name)
                        return render(request, 'viewproducts.html',{'product': product,'images': images,   'offer':ofr, 'offer_category':offer_category, 'offer_product': offer_product})
        return render(request, 'viewproducts.html', {'product': product, 'images': images,  'offer':ofr, 'offer_category':offer_category, 'offer_product': offer_product})
    else:
        return redirect('home')
 


# From Add to Cart btn
def addtocart(request):
    pid = request.GET['pid']

    product = Product.objects.get(id=pid)
    offers = Offers.objects.all()
    
    uid = request.user
    if UserCart.objects.filter(product=pid, user=uid).exists():
        cart = UserCart.objects.get(product=pid, user=uid)
        cart.quantity = cart.quantity+1
        cart.save()
        return redirect('mycart')
    else:
        global offerprice
        price = 0
        offerprice=product.selling_price
        for offer in offers:
            
            print(offerprice)  
            category=Category.objects.get(product=pid)  
            if offer.product == product or offer.category == category :
                if offer.is_active==True:
                    offamount = product.selling_price * offer.offer / 100

                    if offamount > offer.max_value:
                    
                        price = product.selling_price - offer.max_value
                        if price < offerprice:
                        
                            offerprice=price
                    else:
                    
                        price = product.selling_price - offamount
                    
                        if price < offerprice:
                            offerprice=price
                
        cart = UserCart.objects.create(user=uid, product=product, quantity=1, price_with_offer=offerprice)
        cart.save_base()
        return redirect('mycart')    


# Already in Cart but need to + and -
def addtomycart(request):
    print(request.method)
    if request.method == 'POST':
        if request.user.is_authenticated: 
            uid = request.user
            prod_id = int(request.POST.get('product_id'))
            print(prod_id)
            if UserCart.objects.filter(product=prod_id, user=uid).exists():
                prod_qty = int(request.POST.get('product_qty')) 
                print(prod_qty)
                cart = UserCart.objects.get(product=prod_id, user=uid)
                cart.quantity=prod_qty
                cart.save()  
                return redirect('mycart')

        else:
            return redirect('loginpage')
    
    
    else:
        if request.user.is_authenticated:
            user = request.user
            cart = UserCart.objects.filter(user=user).order_by('-id')
            offers = Offers.objects.all()
            if len(cart) == 0:
                print('working')
                empty = "Cart is Empty"
                cartlen=len(cart)
                return render(request, 'mycart.html', {'empty': empty,'cartlen': cartlen,'offers': offers,})
            else:
                for crt in cart:
                    print("catid =", crt.id)

            print(len(cart))
            for i in range(len(cart)):
                 if cart[i].quantity < 1:
                    cart[i].delete()
        else:
            return redirect('loginpage')

        if len(cart) == 0:
            print('working')
            empty = "Cart is Empty"
            cartlen=len(cart)
            return render(request, 'mycart.html', {'empty': empty,'cartlen': cartlen,'offers': offers,})
        else:
  
            subtotal = 0
            for i in range(len(cart)):
                if cart[i].price_with_offer !=0:
                        x = cart[i].price_with_offer*cart[i].quantity
                        subtotal = subtotal+x
                    
                else:
                        x = cart[i].product.selling_price*cart[i].quantity
                        subtotal = subtotal+x
                    
 
            shipping = 0
            total = subtotal + shipping
            print(total)
            if request.user.first_name !='':
               realuser=True
               
               return render(request, 'mycart.html', {'cart': cart, 'subtotal': subtotal, 'total': total,'realuser':realuser,'offers': offers,})
            else:
                return render(request, 'mycart.html', {'cart': cart, 'subtotal': subtotal, 'total': total,'offers': offers,})



def viewcart(request):                                    #to render the cart with its contents
   cart=UserCart.objects.filter(user=request.user)
   offers = Offers.objects.all()

   context={ 'cart':cart} 
   if len(cart)==0:
     empty="Cart is empty"
     context={ 'cart':cart,'empty':empty} 
     return render(request,'mycart.html',context)
   else:
     subtotal=0
     for i in range(len(cart)):
        x=cart[i].product.selling_price*cart[i].quantity
        subtotal=subtotal+x
        print(subtotal)
       
     context={ 'cart':cart,'subtotal':subtotal,'offers':offers} 
    
     return render(request,'mycart.html',context)
 
 


def up(request):                                 #to increase the cart item
  id=request.GET['id']
  cart = UserCart.objects.get(id=id)
  cart.quantity = cart.quantity+1
  cart.save()
  quantity=cart.quantity
  crt = UserCart.objects.filter(user=request.user)
  subtotal=0
  for i in range(len(crt)):
    x=crt[i].product.selling_price*crt[i].quantity
    subtotal=subtotal+x
  print(subtotal)
  return JsonResponse({'data':quantity,'total':subtotal})


def down(request):                               #to decrease the cart item
  id=request.GET['id']
  cart = UserCart.objects.get(id=id)
  cart.quantity = cart.quantity-1
  cart.save()
  quantity=cart.quantity
  crt = UserCart.objects.filter(user=request.user)
  subtotal=0
  for i in range(len(crt)):
    x=crt[i].product.selling_price*crt[i].quantity
    subtotal=subtotal+x
  print(subtotal)
  return JsonResponse({'data':quantity,'total':subtotal})


def removecart(request):           #remove from the cart
  id=request.GET['id']
  cart = UserCart.objects.get(id=id)
  cart.delete()
  return redirect('cart')
      
      


@login_required(login_url='loginpage')
def checkout(request):
    print('checkput')
    if request.method == 'POST' and 'address_id' in request.POST :
    
        address_id = request.POST['address_id']
        address = Address.objects.get(id=address_id)
        cart = UserCart.objects.filter(user=request.user)
        subtotal = 0
        for i in range(len(cart)):
                if cart[i].price_with_offer !=0:
                    x = cart[i].price_with_offer*cart[i].quantity
                    subtotal = subtotal+x
                else:
                    x = cart[i].product.selling_price*cart[i].quantity
                    subtotal = subtotal+x
        shipping = 0
        total = subtotal+shipping
        return render(request, 'payment.html', {'subtotal': subtotal, 'total': total, 'addresses': address,'cart':cart})     
   
    elif request.method == 'POST' and 'code' in request.POST:
        user = request.user
        method = request.POST['payment']
        amount = request.POST['amount']
        address = request.POST['address']
        addresses=Address.objects.get(id=address)
        cart = UserCart.objects.filter(user=user)
        print("address",address)
        total = float(request.POST['amount'])
        code = request.POST['code']
        if Coupon.objects.filter(code=code).exists():
            subtotal = 0
            for i in range(len(cart)):
                if cart[i].cancel != True:
                    if cart[i].price_with_offer !=0:
                        x = cart[i].price_with_offer*cart[i].quantity
                        subtotal = subtotal+x
                    else:
                        x = cart[i].product.selling_price*cart[i].quantity
                        subtotal = subtotal+x
            shipping = 0
            message=False
            coupon = Coupon.objects.get(code=code)
            if total>coupon.min_amount:
                total = total-coupon.discount
            else:
                message = "Minimum Amount is not reached"    
            return render(request, 'payment.html', { 'subtotal':subtotal,'total': total,'message':message, 'addresses': addresses,'cart':cart, 'code':code, 'offer':coupon})
        else:
             message="Invalid"
             subtotal = 0
             for i in range(len(cart)):
                if cart[i].price_with_offer !=0:
                    x = cart[i].price_with_offer*cart[i].quantity
                    subtotal = subtotal+x
                else:
                    x = cart[i].product.selling_price*cart[i].quantity
                    subtotal = subtotal+x
             shipping = 0
             total = subtotal+shipping 
             messages.info(request,"No Such Coupons Exists") 
             print(message)
             return render(request, 'payment.html', { 'message':message, 'addresses': addresses,'subtotal': subtotal, 'total': total})

    else:
        print('else===')
        user = request.user
        cart = UserCart.objects.filter(user=user)
        addresses = Address.objects.filter(user=user)
        print(addresses)
        print(cart)
        subtotal = 0
        for i in range(len(cart)):
                if cart[i].price_with_offer !=0:
                    x = cart[i].price_with_offer*cart[i].quantity
                    subtotal = subtotal+x
                else:
                    x = cart[i].product.selling_price*cart[i].quantity
                    subtotal = subtotal+x
        shipping = 0
        total = subtotal+shipping
        return render(request, 'checkout.html', {'subtotal': subtotal, 'total': total, 'addresses': addresses})      
      
@login_required(login_url='loginpage')
def addaddress(request):

    if request.method == 'POST':
        user = request.user
        name = request.POST['name']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        address = Address.objects.create(
            name=name, phone=phone, address=address, city=city, state=state, pincode=pincode, user=user)
        address.save()
        return redirect('checkout')
    else:
        return render(request, 'addaddress.html')   
      
          
  
@login_required(login_url='loginpage')
def myorder(request):
    order = Order.objects.filter(user=request.user).order_by('-id')
    cart = UserCart.objects.filter(user=request.user)
    oldcart = AdminCart.objects.filter(user=request.user)
    if len(order) == 0:
        empty = "No Order Placed"
        return render(request, 'myorders.html', {'empty': empty})
    subtotal = 0
    for i in range(len(cart)):
        x = cart[i].product.selling_price*cart[i].quantity
        subtotal = subtotal+x
    shipping = 0
    total = subtotal + shipping
    return render(request, 'myorders.html', {'orders': order, 'cart': oldcart, 'total': total})


def cancelorder(request):
    user = request.user
    id = request.GET['id']
    Order.objects.filter(id=id).update(status='Cancelled', cancel=True)  
    return redirect('myorder')

def myprofile(request):
    user = request.user
    address = Address.objects.filter(user=user)
    return render(request, 'profile.html', {'user': user, 'address': address})
  
def cod(request):
    user = request.user
    order = Order.objects.filter(user=request.user).order_by('-id')
    cart = UserCart.objects.filter(user=request.user)
    oldcart = AdminCart.objects.filter(user=request.user)
    address = Address.objects.filter(user=user)
    print("heyy")
    return render(request, 'cod.html', {'orders': order, 'cart': oldcart,})

def razorpay(request):
    cart = UserCart.objects.filter(user=request.user)
    subtotal = 0
    print(subtotal)
    for i in range(len(cart)):
        x = cart[i].product.selling_price*cart[i].quantity
        subtotal = subtotal+x
    shipping = 0
    total = subtotal+shipping
    return JsonResponse({
                         'total': total,})


def payment(request):
    if request.method == 'POST':
        user = request.user
        method = request.POST['payment']
        amount = request.POST['amount']
        print(amount)
        cart = UserCart.objects.filter(user=user)
        address = request.POST['address']
        print("address",address)
        address = Address.objects.get(id=address)
        subtotal = 0
        for i in range(len(cart)):
            x = cart[i].product.selling_price*cart[i].quantity
            subtotal = subtotal+x
        shipping = 0
        total = subtotal + shipping
        crt = UserCart.objects.filter(user=user)
        print(method)
        order = Order.objects.create(
            user=user, address=address, amount=amount, method=method)
        order.save()
        for i in range(len(cart)):
            oldcart = AdminCart.objects.create(
                user=user, quantity=crt[i].quantity, product=crt[i].product, order=order)
            oldcart.save()
        cart.delete()
        prdcts=AdminCart.objects.filter(order=order)
        for i in range(len(prdcts)-1):
            p=Product.objects.filter(id=prdcts[i].product.id)        
            Product.objects.filter(id=prdcts[i].product.id).update(quantity=p[i].quantity-prdcts[i].quantity)
        success = True
        product = Product.objects.all()
        categories = Category.objects.all()
        print("==",categories)
        payMode=request.POST['payment']
        if payMode=='Razorpay' or  payMode=='Paypal':
            print(payMode)
            return JsonResponse({'status' : "Your Order has been placed successfully"})
        return render(request, 'cod.html', {'user': user, 'products': product, 'categories': categories, 'success': success})
    else:
        user = request.user
        cart = UserCart.objects.filter(user=user)
        subtotal = 0
        for i in range(len(cart)):
            x = cart[i].product.selling_price*cart[i].quantity
            subtotal = subtotal+x
        shipping = 0
        total = subtotal + shipping
        return render(request, 'payment.html', {'subtotal': subtotal, 'total': total, 'cart': cart})                         



@login_required(login_url='loginpage')
def returnorder(request):
    if request.method == 'POST':
        id=int(request.GET['id'])
        print(id)
        order = Order.objects.get(id=id)
        user = request.user
        status = 'Return Requested'
        reason = request.POST['reason']
        order = Order.objects.filter(id=id).update(status=status, reason=reason)
        print(reason)
        print(order)
        print(status)
        return redirect('myorder')   

    else:
        id=int(request.GET['id'])
        print(id)
        context={'id':id}
        return render(request,'returnorder.html',context)
          

 