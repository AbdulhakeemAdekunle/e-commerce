from typing import Any
from django.contrib import admin
from django.db.models import F
from django.db.models.aggregates import Count, Sum
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.urls import reverse
from . import models

admin.site.site_header = 'Store Admin'
admin.site.index_title = 'Admin'

# Register your models here.

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category']
    list_display = ['name', 'price', 'stock_status', 'category']
    list_per_page = 15
    list_filter = ['category', 'created_date']
    ordering = ['stock_quantity']
    search_fields = ['name']

    def stock_status(self, product):
        if product.stock_quantity < 10:
            return 'Low'
        return 'OK'
    
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related('category')


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    list_per_page = 15
    search_fields = ['title']

    def products_count(self, category):
        url = reverse('admin:store_product_changelist') + f'?category__id__exact={category.id}'
        return format_html('<a href="{}">{}</a>', url, category.products_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        ).prefetch_related('products')


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    list_select_related = ['user']
    list_per_page = 15
    ordering = ['-orders', 'user__first_name', 'user__last_name']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']

    def orders(self, customer):
        url = reverse('admin:store_order_changelist') + f'?customer__id__exact={customer.id}'
        return format_html('<a href="{}">{}</a>', url, customer.orders_count)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(
            orders_count = Count('orders')
        ).select_related('user')\
        .prefetch_related('orders')


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id','first_name', 'last_name', 'email', 'is_staff', 'is_active']
    list_editable = ['is_active', 'is_staff']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['first_name']


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ['product']
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer']
    list_display = ['id', 'customer', 'placed_at', 'payment_status', 'total_amount']
    list_per_page = 10

    def total_amount(self, order):
        return order.total_amount
    
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request)\
            .annotate(
                total_amount=Sum(
                   F('items__quantity') * F('items__unit_price') 
                )
            )


