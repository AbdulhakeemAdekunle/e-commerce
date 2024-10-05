from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Review, Customer, Order, OrderItem
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from pprint import pprint

# Create your views here.

class ProductViewSet(ModelViewSet):
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

    def destroy(self, request, *args, **kwargs):
        product = Product.objects.get(pk=self.kwargs['pk'])
        if product.ordered.count() > 0:
            return Response({'error': 'Cannot delete this product because it is associated with an existing order'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
        

class CategoryViewSet(ModelViewSet):
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
    

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_pk', None)
        reviews_list = Review.objects.all()
        if product_id:
            reviews = Review.objects.filter(product_id=product_id)
            return reviews
        return reviews_list

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}