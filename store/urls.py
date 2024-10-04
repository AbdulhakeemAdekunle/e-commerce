from django.urls import path
from . import views
urlpatterns = [
    path('products/', views.ProductList.as_view(), name='products'),
    path('products/<int:id>/', views.ProductDetail.as_view(), name='product'),
    path('categories/', views.CategoryList.as_view(), name='categories'),
    path('categories/<int:id>', views.CategoryDetail.as_view(), name='category')
]