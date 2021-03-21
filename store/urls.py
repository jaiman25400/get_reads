from django.urls import path

from . import views
#from .views import  ItemDetailView


urlpatterns = [
	#Leave as empty string for base url
	path('', views.stores, name="stores"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
	path('register/', views.registerPage, name="register"),
	path('login/', views.loginPage, name="login"),  
	path('logout/', views.logoutUser, name="logout"),
	path('order/', views.order, name="order"),
#	path('detail/<slug>/',ItemDetailView.as_view(), name='detail'),
    path('<slug:slug>/',views.product_details, name='product_details'),

]