from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from authsys.models import User
from .validators import validate_file_size
# Create your models here.


# create a category model with fields: id, title
class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']

# create a product model with fields: id, name, description, price, category_id(FK-category model), stock_quantity, created_date, discount
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    stock_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    created_date = models.DateField(auto_now=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)

    def __str__(self):
        return self.name

    # create a method to apply discount by subtracting the discounted value from the initial price.
    @property
    def discounted_price(self):
        if self.discount:
            discount_factor = (100 - float(self.discount))/100
            return round(self.price * discount_factor, 2)
        return self.price
    

# create a product image model with fields: id, product_id(FK-product model), image
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='store/images', validators=[validate_file_size])


# create a customer model with fields: id, user_id(OneToOneField-user model), phone, birth_date, membership
class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255, null=True)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)

    # define method to return first_name of the related user when customer.first_name is accessed
    @property
    def first_name(self):
        return self.user.first_name
    
    # define method to return last_name of the related user when customer.last_name is accessed
    @property
    def last_name(self):
        return self.user.last_name
    
    # define method to return email of the related user when customer.email is accessed
    @property
    def email(self):
        return self.user.email
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    

# create a address model with fields: id, street, city, customer_id(FK-customer model)
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')


# create a wished item model with fields: id, customer_id(FK-customer model), product_id(FK-product model), date
class WishedItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='liked')
    date = models.DateField(auto_now_add=True)


# create a review model with fields: id, customer_id(FK-customer model), product_id(FK-product model), summary, details, rating, date
class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    summary = models.CharField(max_length=255)
    details = models.TextField(null=True, blank=True)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.summary}'


# create a order model with fields: id, customer_id(FK-customer model), payment_status, placed_at
class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')

    # define a method to get the total price of the items in the order
    @property
    def total_price(self):
        return sum(item.quantity * item.unit_price for item in self.items.all())
    

# create an order item model with fields: id, customer_id(FK-customer model), product_id(FK-product model), date
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='ordered')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # define a method to get the total price of a single order item based on its quantity
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    
    # override the inbuilt save() method to determine how an order item instance is being saved.
    # unit_price in an order item should be strictly equal to the product price at the time of creating the order
    def save(self,*args, **kwargs) -> None:
        if self.unit_price is None:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)


# create a cart model with fields: id, created_date
class Cart(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)


# create a cart item model with fields: id, cart_id(FK-cart model), product_id(FK-product model), quantity
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [['cart', 'product']]

