from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,date
from django.shortcuts import reverse
from django.db.models import Avg, Count
from django.forms import ModelForm
# Create your models here.

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)

	def __str__(self):
		return self.email


class Category(models.Model):
	name = models.CharField(max_length=200)

	@staticmethod
	def get_all_categories():
		return Category.objects.all()
		
	def __str__(self):
		return self.name


class Product(models.Model):
	name = models.CharField(max_length=200)
	price = models.FloatField()
	digital = models.BooleanField(default=False,null=True, blank=True)
	image = models.ImageField(null=True, blank=True)
	description = models.TextField("Description",max_length=500  )
	is_featured = models.BooleanField("Featured",default=False)
	on_sale = models.BooleanField("On Sale",default=False )
	discounted_price = models.DecimalField("Price after discount",decimal_places=2,max_digits=5,null=True,  blank=True)
	slug = models.SlugField(max_length=150)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True,default=1)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("detail", kwargs={
			'slug': self.slug
		})

	def get_rating(self):
		total = sum(int(review['stars']) for review in self.reviews.values())

		if self.reviews.count() > 0:
			return total / self.reviews.count()
		else:
			return 0

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url

	@staticmethod
	def get_product_by_id(category_id):
		if category_id:
			return Product.objects.filter(category=category_id)
		else:
			return Product.objects.all()
class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)
	#status = models.BooleanField(default=False,null=True, blank=True)
	
	def __str__(self):
		return str(self.id)
	
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

class OrderItem(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)
	status = models.BooleanField(default=False,null=True, blank=True)
	#category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,default=1)
	
	@staticmethod
	def get_orderitem_by_customer(customer_id):
		return OrderItem\
			.objects\
			.filter(customer = customer_id)\
			.order_by('-date_added')

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address

class ProductReview(models.Model):
	product = models.ForeignKey(Product,related_name='reviews',on_delete=models.CASCADE)
	user = models.ForeignKey(User,related_name='reviews', null=True, blank=True, on_delete=models.CASCADE)
	content = models.TextField(blank=True,null=True)
	stars = models.IntegerField()
	date_added = models.DateTimeField(auto_now_add=True)