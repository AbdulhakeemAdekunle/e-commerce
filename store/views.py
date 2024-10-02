from django.shortcuts import render
from django.db import transaction
from django.http.response import HttpResponse
from django.contrib.contenttypes.models import ContentType
from review.models import Review
from .models import Category, Product, Customer, WishedItem, Review, Address, User, Order, OrderItem, Cart, CartItem 

# Create your views here.

def products(request):
    products = Product.objects.all()
    if request.method == 'GET':
        return render(request, 'index.html', {'greet': 'hello', 'products': products})


def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        context = {'categories': categories}
        return render(request, 'category_list.html', context)
    
    if request.method == 'POST':
         title = request.POST.get('title')
         category = Category.objects.create(title=title)
         context = {'category': category}
         return render(request, 'category_list.html', context)
    
    # context = {'category': category}
    # return render(request, 'category.html', context)
    

def category(request, id):
     if request.method == 'GET':
        category = Category.objects.get(id=id)
        context = {'category': category}
        return render(request, 'category_list.html', context)
        