from django.shortcuts import  get_object_or_404,render,redirect
from django.http import JsonResponse
import json
from django.http import HttpResponse, HttpResponseRedirect
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .form import *
#from  django.views.generic import ListView,DetailView

def stores(request):
	data = cartData(request)
	categories = Category.get_all_categories() 
	cartItems = data['cartItems']
	
	categoryID = request.GET.get('category')
	if categoryID:
		products = Product.get_product_by_id(categoryID)
	else:
		products = Product.objects.all()	
	#products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems,'categories':categories}
	return render(request, 'store/stores.html', context)

#class ItemDetailView(DetailView):

#    model = Product
#    product1 = Product
#	context_object_name = 'product'	
	
#    def post(self,request):
#        if request.method == POST and request.user.is_authenticated:
#            stars = request.POST.get('stars',3)
 #           content = request.POST.get('content','')
 #           review = ProductReview.objects.create(product = product1,user = request.user,stars = stars,content = content)
 #           return redirect('/')

#	template_name = "store/description.html"

def product_details(request,slug):
	product = get_object_or_404(Product, slug=slug)
	if request.method == 'POST' and request.user.is_authenticated:
		stars = request.POST.get('stars', 3)
		content = request.POST.get('content', '')

		review = ProductReview.objects.create(product=product, user=request.user, stars=stars, content=content)

		return redirect('/',slug=slug)

	context = {
		'product':product,
	}
	return render(request,'store/product_details.html',context)
	#def get_context_data(self, **kwargs):
	#	data = cartData(self.request)
	#	cartItems = data['cartItems']
	#	context = {'cartItems':cartItems}
	#	return context



def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(customer=customer,order=order, product=product)# if order item already exist we want to change it  

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total']) # Checkout.html Form and Total is mentioned
	if total != 0:
		order.transaction_id = transaction_id
		order.date_ordered =  datetime.now()
		if total == order.get_cart_total:
			order.complete = True
		order.save()
	else:
		return JsonResponse('Add An item to cart..', safe=False)
	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		date_added= datetime.now(),
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

def registerPage(request):
	if request.user.is_authenticated:
		return redirect('store')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			username=request.POST['username']
			password1=request.POST['password1']
			password2=request.POST['password2']
			email=request.POST['email']
			form = CreateUserForm(request.POST)
			if form.is_valid():
				if User.objects.filter(username=username).exists():
					messages.info(request,'Username Taken')
					return redirect('register')
				elif User.objects.filter(email=email).exists():
					messages.info(request,'Email Taken')
					return redirect('register')
				else: 
					user = form.save()
					name = request.POST['username']
					email = request.POST['email']
					Customer.objects.create(
					user = user,email=email,name=name)	
					print('User Created')
					return redirect('login')
		
			#	user = form.save()
			#	name = request.POST['username']
			#	email = request.POST['email']
			#	Customer.objects.create(
			#		user = user,email=email,name=name
			#	)
				
				
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + user)# flash msg would popup

				return redirect('login')
		
		
		context = {'form':form}
		return render(request, 'store/register.html', context)
def loginPage(request):
	if request.user.is_authenticated:
		return redirect('stores')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')

			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('stores')
			else:
				messages.info(request, 'Username OR password is incorrect')

		context = {}
		return render(request, 'store/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')

def order(request):
	data = cartData(request)
	customer = request.user.customer
	order = OrderItem.get_orderitem_by_customer(customer)
	#item = order.orderitem_set.all()
	cartItems = data['cartItems']
	date_ordered = datetime.now()
	#print(order.save())
	context = {'orders':order,'cartItems':cartItems}
	return render(request,'store/orders.html',context)
