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
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('users', views.UserViewSet, basename='users')


products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(carts_router.urls)),
    path('login', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register')
]

# urlpatterns = [
#     path('products/', views.ProductList.as_view(), name='products'),
#     path('products/<int:pk>/', views.ProductDetail.as_view(), name='product'),
#     path('categories/', views.CategoryList.as_view(), name='categories'),
#     path('categories/<int:pk>', views.CategoryDetail.as_view(), name='category')
# ]