from django.conf import settings
from rest_framework import serializers
from .models import(
    ProductCategory,
    Product,
    ProductImage,
    UserAddress,
    Cart,
    CartItem
)

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    # image_url = serializers.URLField(source='image', read_only=True)
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductImageURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name",read_only=True)
    images_url = serializers.SerializerMethodField()
    class Meta:
        model = Product
        # fields = '__all__'
        fields = ['id', 'images_url', 'upc', 'name', 'description', 'price', 'quantity', 'cart_quantity', 'category_name', 'category', 'updated_at']

    def get_images_url(self, obj):
        request = self.context.get('request')
        image = obj.images.first()
        if image and request is not None:
            return request.build_absolute_uri(image.image.url)
        return None



class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'house_no', 'street', 'city', 'postal_code', 'state', 'country', 'is_default']
        read_only_field = ['user']

# class CartItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CartItem
#         fields = '__all__'

# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Cart
#         fields = '__all__'

class CartProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class CartProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    images = CartProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'images', 'upc', 'name', 'description', 'price', 'quantity', 'category_name', 'category', 'created_at', 'updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()
    # user_address = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_id', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.quantity * obj.product.price
    
    def get_user_address(self, obj):
        if obj.user_address:
            return {
                "id": obj.user_address.id,
                "address": obj.user_address.address,
                "city": obj.user_address.city,
                "state": obj.user_address.state,
                "zip_code": obj.user_address.zip_code,
                "is_default": obj.user_address.is_default
            }
        return None
    
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'quantity', 'total_price', 'created_at', 'updated_at']

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.item.all())

    def get_total_price(self, obj):
        return sum(item.quantity * item.product.price for item in obj.items.all())


