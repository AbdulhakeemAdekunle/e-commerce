from django.urls import path
from .views import products, category, category_list

urlpatterns = [
    path('products/', products, name='products'),
    path('categories/', category_list, name='categories'),
    path('categories/<int:id>', category, name='category')
]