from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    upc = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    cart_quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    # status = models.CharField(max_length=20, null=True, blank=True)
    user_address = models.CharField(max_length=10, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    # is_payment = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)

# class ProductReview(models.Model):
#     product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     description = models.TextField()
#     rating = models.PositiveSmallIntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='addresses', on_delete=models.CASCADE)
    house_no = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    state = models.CharField(max_length=50,null=True, blank=True)
    country = models.CharField(max_length=100, default="India")
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.house_no}, {self.street}, {self.city}, {self.postal_code}, {self.country}"
    
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.mobile}"
    
class CartItem(models.Model):
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('cancelled', 'Cancelled'),
        ('processing', 'Processing'),
    ]
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, related_name='cart_item')
    quantity = models.PositiveIntegerField(default=1)
    user_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ordered")
    transaction_id = models.CharField(max_length=100, null=True, blank=True, help_text="Payment made by RazorPay")
    is_payment = models.BooleanField(default=False)

    def __str__(self):
        product_names = ", ".join([product.name for product in self.product.all()])
        return f"{self.quantity} x [{product_names}] - {self.status}"
    
# class Order(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     billing_address = models.ForeignKey(UserAddress, related_name='billing_orders', on_delete=models.SET_NULL, null=True)
#     shipping_address = models.ForeignKey(UserAddress, related_name='shipping_orders', on_delete=models.SET_NULL, null=True)


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()
#     ordered_price = models.DecimalField(max_digits=10, decimal_places=2)


# class Payment(models.Model):
#     order = models.OneToOneField(Order, on_delete=models.CASCADE)
#     status = models.CharField(max_length=50)
#     updated_at = models.DateTimeField(auto_now=True)
