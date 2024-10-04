from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.db.models import ProtectedError, Count
from django.http.response import HttpResponse
from django.contrib.contenttypes.models import ContentType
from .models import Category, Product, Customer, Order, OrderItem
from .serializers import ProductSerializer, CategorySerializer, CreateCategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pprint import pprint

# Create your views here.

@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        query = request.query_params.get('q', None)
        category_title = request.query_params.get('category', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        stock_avail = request.query_params.get('in_stock', None)
        products = Product.objects.select_related('category').all()
        
        if query:
            products = products.filter(name__icontains=query)

        if category_title:
            products = products.filter(category__title=category_title)

        if min_price and max_price:
            products = products.filter(price__gte=min_price, price__lte=max_price)
        
        if stock_avail:
            products = products.filter(stock_quantity__gt=0)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        if product.ordered.count() > 0:
            return Response({'error': 'Cannot delete this product because it is associated with an existing order'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all().\
            annotate(products_count=Count('products'))
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, id):
    category = get_object_or_404(Category.objects.all().\
            annotate(products_count=Count('products')), pk=id)
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if category.products.count() > 0:
            return Response({'error':'Can not delete category because it has one or more products'})
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)