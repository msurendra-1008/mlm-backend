from django.contrib import admin

# Register your models here.
from .models import ProductCategory, Product, ProductImage, Cart, CartItem, UserAddress, Payment

admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(UserAddress)
admin.site.register(Payment)