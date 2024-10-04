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
from rest_framework.views import APIView
from pprint import pprint

# Create your views here.

class ProductList(APIView):
    def get(self, request):
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

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetail(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if product.ordered.count() > 0:
            return Response({'error': 'Cannot delete this product because it is associated with an existing order'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(status=status.HTTP_204_NO_CONTENT)

        

class CategoryList(APIView):
    def get(self, request):
        categories = Category.objects.all().\
            annotate(products_count=Count('products'))
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetail(APIView):
    def get(self, request, id):
        category = get_object_or_404(Category.objects.all().\
            annotate(products_count=Count('products')), pk=id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    def put(self, request, id):
        category = get_object_or_404(Category.objects.all().\
            annotate(products_count=Count('products')), pk=id)
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, id):
        category = get_object_or_404(Category.objects.all().\
            annotate(products_count=Count('products')), pk=id)
        if category.products.count() > 0:
            return Response({'error':'Can not delete category because it has one or more products'})
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)