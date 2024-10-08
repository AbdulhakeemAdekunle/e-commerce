from django.urls import path, include
from . import views
from rest_framework_nested import routers
from pprint import pprint
from .models import Product, Review


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('reviews', views.ReviewViewSet, basename='reviews')
router.register('carts', views.CartViewSet, basename='carts')
router.register('cartitems', views.CartItemViewSet, basename='cartitems')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(carts_router.urls))
]

# urlpatterns = [
#     path('products/', views.ProductList.as_view(), name='products'),
#     path('products/<int:pk>/', views.ProductDetail.as_view(), name='product'),
#     path('categories/', views.CategoryList.as_view(), name='categories'),
#     path('categories/<int:pk>', views.CategoryDetail.as_view(), name='category')
# ]