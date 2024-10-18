from django.db import transaction
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework import status
from .models import Category, Product, ProductImage, Review, Cart, CartItem, Customer
from .filters import ProductFilter
from .paginations import DefaultPagination
from .serializers import ProductSerializer, ProductImageSerializer, CreateProductSerializer, UpdateProductSerializer, CategorySerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer
from authsys.models import User

# Create your views here.

# ProductViewSet that supports all request methods inheritting from ModelViewset
class ProductViewSet(ModelViewSet):
    http_method_names = ['get', 'patch', 'post', 'delete']
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['name', 'category__title']
    ordering_fields = ['price', 'stock_quantity']
    queryset = Product.objects.prefetch_related('images').all()

    # override the destroy() method to check for some condition before deleting a product. (Checks if the product is included in an order to prevent deletion)
    def destroy(self, request, *args, **kwargs):
        product = Product.objects.get(pk=self.kwargs['pk'])
        if product.ordered.count() > 0:
            return Response({'error': 'Cannot delete this product because it is associated with an existing order'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
    # override the get_serializer_class method to return different serializers on different requests
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateProductSerializer
        elif self.request.method == 'PATCH':
            return UpdateProductSerializer
        elif self.request.method == 'GET':
            return ProductSerializer
    
    # override the get_permission method to allow only an authorized user (admin) to perform POST, PATCH, DELETE method. Otherwise only a GET method is allowed
    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]


# ProductImageViewSet that supports all request methods inheritting from ModelViewset
class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    # method get a serializer context (url kwargs) and pass it to the serializer
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    
    # override the get_queryset method to return only images specific to a product instance
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])


# CategoryViewSet that supports all request methods inheritting fro ModelViewset
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all().annotate(products_count=Count('products'))
    serializer_class = CategorySerializer
    pagination_class = DefaultPagination

    # override the destroy method to check for some conditions before deleting a category. (Checks if the category has existing products to prevent deletion)
    def destroy(self, request, *args, **kwargs):
        category = get_object_or_404(
            Category.objects.all().\
            annotate(products_count=Count('products')), pk=self.kwargs['pk'])
        if category.products.count() > 0:
            return Response({'error':'Can not delete category because it has one or more products'})
        return super().destroy(request, *args, **kwargs)
    

# ReviewViewSet that supports all request methods inheritting from ModelViewset
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    # override the get_queryset method to return only reviews specific to a product instance
    def get_queryset(self):
        product_pk = self.kwargs.get('product_pk', None)
        reviews_list = Review.objects.all()
        if product_pk:
            reviews = Review.objects.filter(product_id=product_pk)
            return reviews
        return reviews_list

    # method get a serializer context (url kwargs) and pass it to the serializer
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
    

# CustomerViewSet that supports all request methods inheritting from ModelViewset
class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated] # A user must be authenticated in order to create a customer record

    # override the get_queryset method to return only the customer record specific to the logged in user
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Customer.objects.all()
        else:
            return Customer.objects.filter(user=self.request.user)

    # override the perform_create method to get the user from the request and associate it with the customer serializer
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
    
    