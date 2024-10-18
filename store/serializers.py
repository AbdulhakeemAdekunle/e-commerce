from decimal import Decimal
from django.db.models import Count
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from .models import Product, Category, Review, Cart, CartItem, Customer, ProductImage


# CategorySerializer class, that gets rendered on the api endpoint for GET request: store/categories 
class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'title', 'products_count']


# CreateCategorySerializer class, that handles the api endpoint for POST request: store/categories 
class CreateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']


# ProductImageSerializer class, that handles the api endpoint for POST request: store/products/id/images 
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    # override the create() method in ModelSerializer class, to add a serializer context while creating the serializer
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)
    

# ProductSerializer class, that handles the api endpoint for GET request: store/products 
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'images', 'stock_quantity', 'category']


# UpdateProductSerializer class, that handles the api endpoint for PUT request: store/products/id
class UpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['stock_quantity', 'price',]


# CreateProductSerializer class, that handles the api endpoint for POST request: store/products 
class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock_quantity']


# ReviewSerializer class, that handles the api endpoint for POST request: store/products/id/reviews 
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'customer', 'summary', 'details', 'rating', 'date']

    # override the create() method in ModelSerializer class, to add a serializer context while creating the serializer
    def create(self, validated_data):
        product_pk = self.context['product_pk']
        return Review.objects.create(product_id=product_pk, **validated_data)
    

# CartItemProductSerializer class, that renders the 'product' field as a nested object in the CartItem on the api endpoint for GET request: store/cartitems/ 
class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']
    

# CartItemSerializer class, that handles the api endpoint for GET request: store/cartitems 
class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer() #renders product field as a nested object
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    # custom method to calculate the total_price of a cart item based on the quantity.
    def get_total_price(self, cartitem):
        return cartitem.product.price * cartitem.quantity


# AddCartItemSerializer class, that handles the api endpoint for POST request: store/cartitems 
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    # custom method to check the existence of product_id to ensure the product exists in the database before adding it to cart.
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given id')
        return value

     # override the save() method in BaseSerializer class, to handle creating and updating of a model f
    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']
        
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            # Update an existing item if cart item object exists in the database.
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # Create a new item if no cart item object was found
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance


# UpdateCartItemSerializer class, that handles the api endpoint for PUT request: store/cartitems/id 
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']



# CartSerializer class, that handles the api endpoint for POST request: store/carts
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True) #renders items field as a nested object
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    # custom method to calculate the total_price of all items in a cart
    def get_total_price(self, cart):
        return sum(item.product.price * item.quantity for item in cart.items.all())
    

# CustomerSerializer class, that handles the api endpoint for POST/GET requests: store/customers
class CustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone', 'birth_date']

    # custom method to return customer's first_name from the related user model
    def get_first_name(self, customer):
        return customer.user.first_name
    
    # custom method to return customer's last_name from the related user model
    def get_last_name(self, customer):
        return customer.user.last_name