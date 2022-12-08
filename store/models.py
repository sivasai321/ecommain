from email.policy import default
from importlib import import_module
from unicodedata import category
from django.db import models
import os
import datetime
from store.mixins import *
from django.db import models
import uuid
from django.db import models
from django.contrib.auth.models import User
from adminapp.models import *


def get_file_path(request,filename):
  original_filename=filename
  nowTime=datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
  filename="%s%s" % (nowTime,original_filename)
  return os.path.join('assets/',filename)  


class Category(models.Model):
  slug=models.CharField(max_length=150,null=False, blank=False)
  name=models.CharField(max_length=150,null=False, blank=False)
  image=models.ImageField(upload_to=get_file_path,null=True,blank=True)
  status=models.BooleanField(default=True,help_text='0=default,1=Hidden')
 
  def __str__(self):  #without this it will only show object 1,2,3 etc instead of name
    return self.name
  
class Product(models.Model):
  category=models.ForeignKey(Category,on_delete=models.CASCADE)
  slug=models.CharField(max_length=150,null=False, blank=False)
  name=models.CharField(max_length=150,null=False, blank=False)
  product_image=models.ImageField(upload_to=get_file_path,null=True,blank=True)
  quantity=models.IntegerField(null=False,blank=False)
  small_description=models.CharField(max_length=200, null=False, blank=False)
  description=models.TextField(max_length=300, null=False, blank=False)  
  selling_price=models.FloatField(null=False,blank=False)
  tag=models.CharField(max_length=200, null=False, blank=False)
  status=models.BooleanField(default=True,help_text='0=default,1=Hidden')

  def __str__(self):
    return self.name
  

class Accounts(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.BigIntegerField()
    otp = models.CharField(max_length=100, blank=True, null=True)
    uid=models.CharField(default=f'{uuid.uuid4}',max_length=200)

    
    
    def __str__(self):
        return self.user.username
      
  
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.IntegerField()
  
    def __str__(self):
        return self.user.username 
      

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='pending')
    amount = models.FloatField(default=1)
    method = models.CharField(max_length=100, default='Cash On Delivery')
    cancel = models.BooleanField(default=False)
    reason = models.CharField(max_length=200, default='')


class AdminCart(models.Model):
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=0)      
    
    
class UserCart(models.Model):
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price_with_offer = models.FloatField(default=0)
    cancel = models.BooleanField(default=False)
    
    def __str__(self):
        return self.product.name  
      
      
      
    def __str__(self):
        return self.product.name    

class Offers(models.Model):
    product = models.ForeignKey( Product, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    offer = models.IntegerField()
    offer_type = models.CharField(max_length=200, null=True, blank=True, default='product')
    start_date = models.DateField()
    end_date = models.DateField()
    max_value = models.IntegerField(default=0)
    category = models.ForeignKey( Category, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.product.name
    
class Coupon(models.Model):
    code = models.CharField(max_length=50)
    discount = models.IntegerField()
    start_date = models.DateField()
    min_amount = models.IntegerField(default=0)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Images(models.Model):
    image = models.ImageField(null=True, blank=True, upload_to='assets/images')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.image.url

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url      