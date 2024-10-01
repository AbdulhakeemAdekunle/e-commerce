from django.shortcuts import render
from .models import Product, Category, User
from django.http.response import HttpResponse
from .models import Promotion, Category, Product, Customer, WishedItem, Review, Address, User, Order, OrderItem, Cart, CartItem 

# Create your views here.

def products(request):
    if request.method == 'GET':
        return render(request, 'index.html', {'greet': 'hello'})


def category_list(request):
    if request.method == 'GET':
        context = {'categories': categories}
        categories = Category.objects.all()
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
        