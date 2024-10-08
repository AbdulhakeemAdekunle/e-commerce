from django.db import transaction
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from .models import Category, Product, Review, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from .filters import ProductFilter
from .paginations import DefaultPagination

# Create your views here.

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['name', 'category__title']
    ordering_fields = ['price', 'stock_quantity']
    queryset = Product.objects.all()

    def destroy(self, request, *args, **kwargs):
        product = Product.objects.get(pk=self.kwargs['pk'])
        if product.ordered.count() > 0:
            return Response({'error': 'Cannot delete this product because it is associated with an existing order'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
        

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all().annotate(products_count=Count('products'))
    serializer_class = CategorySerializer
    pagination_class = DefaultPagination

    def destroy(self, request, *args, **kwargs):
        category = get_object_or_404(
            Category.objects.all().\
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
    

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

    def destroy(self, request, pk):
        cart = Cart.objects.get(pk=pk)
        if cart.items.count() > 0:
            return Response({'error': 'Can not delete this cart because it contains some items'})
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = CartItemSerializer

    def get_serializer_class(self):
    
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        cart_id = self.kwargs['cart_pk']
        return CartItem.objects.select_related('product').filter(cart_id=cart_id)
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}