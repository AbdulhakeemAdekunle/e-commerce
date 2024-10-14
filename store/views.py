from django.db import transaction
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework import status
from .models import Category, Product, ProductImage, Review, Cart, CartItem, Customer, Order, OrderItem
from .filters import ProductFilter
from .paginations import DefaultPagination
from .serializers import ProductSerializer, ProductImageSerializer, CreateProductSerializer, UpdateProductSerializer, CategorySerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer
from authsys.models import User

# Create your views here.

class ProductViewSet(ModelViewSet):
    http_method_names = ['get', 'patch', 'post', 'delete']
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['name', 'category__title']
    ordering_fields = ['price', 'stock_quantity']
    queryset = Product.objects.prefetch_related('images').all()

    def destroy(self, request, *args, **kwargs):
        product = Product.objects.get(pk=self.kwargs['pk'])
        if product.ordered.count() > 0:
            return Response({'error': 'Cannot delete this product because it is associated with an existing order'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateProductSerializer
        elif self.request.method == 'PATCH':
            return UpdateProductSerializer
        elif self.request.method == 'GET':
            return ProductSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

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
        product_pk = self.kwargs.get('product_pk', None)
        reviews_list = Review.objects.all()
        if product_pk:
            reviews = Review.objects.filter(product_id=product_pk)
            return reviews
        return reviews_list

    def get_serializer_context(self):
        return {'product_id': self.kwargs.get('product_pk', None)}
    

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
    

class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Customer.objects.all()
        else:
            return Customer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


    # @action(detail=False, methods=['GET', 'PUT'])
    # def me(self, request):
    #     (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
    #     if request.method == 'GET':
    #         seriailzer = CustomerSerializer(customer)
    #         return Response(seriailzer.data)
    #     if request.method == "PUT":
    #         seriailzer = CustomerSerializer(customer, data=request.data)
    #         seriailzer.is_valid(raise_exception=True)
    #         seriailzer.save()
    #         return Response(seriailzer.data)
    
    