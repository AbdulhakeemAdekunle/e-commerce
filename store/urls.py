from django.urls import path
from . import views
urlpatterns = [
    path('products/', views.product_list, name='products'),
    path('products/<int:id>/', views.product_detail, name='product'),
    path('categories/', views.category_list, name='categories'),
    path('categories/<int:id>', views.category_detail, name='category')
]