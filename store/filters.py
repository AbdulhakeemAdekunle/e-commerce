from django_filters import FilterSet
from .models import Product

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'category_id': ['exact'],
            'price': ['gte', 'lte'],
            'stock_quantity': ['gt', 'lt']
        }

    