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
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from pprint import pprint

# Create your views here.

class ProductList(ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        category_title = self.request.query_params.get('category', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        stock_avail = self.request.query_params.get('in_stock', None)
        products = Product.objects.select_related('category').all()
        
        if query:
            products = products.filter(name__icontains=query)

        if category_title:
            products = products.filter(category__title=category_title)

        if min_price and max_price:
            products = products.filter(price__gte=min_price, price__lte=max_price)
        
        if stock_avail:
            products = products.filter(stock_quantity__gt=0)
        return products


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def destroy(self, request, *args, **kwargs):
        product = Product.objects.get(pk=self.kwargs['pk'])
        if product.ordered.count() > 0:
            return Response({'error': 'Cannot delete this product because it is associated with an existing order'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
        

class CategoryList(ListCreateAPIView):
    queryset = Category.objects.all().annotate(
        products_count=Count('products')
    )
    serializer_class = CategorySerializer


class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all().annotate(
        products_count=Count('products')
    )
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        category = get_object_or_404(Category.objects.all().\
            annotate(products_count=Count('products')), pk=self.kwargs['pk'])
        if category.products.count() > 0:
            return Response({'error':'Can not delete category because it has one or more products'})
        return super().destroy(request, *args, **kwargs)