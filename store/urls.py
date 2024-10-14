from django.urls import path, include
from rest_framework_nested import routers
from rest_framework_simplejwt import views as jwt_views
from . import views


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('reviews', views.ReviewViewSet, basename='reviews')
router.register('carts', views.CartViewSet, basename='carts')
router.register('cartitems', views.CartItemViewSet, basename='cartitems')
router.register('customers', views.CustomerViewSet, basename='customer')


products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
products_router.register('images', views.ProductImageViewSet, basename='product-images')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(carts_router.urls)),
]