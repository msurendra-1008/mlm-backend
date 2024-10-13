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
        fields = ['id', 'images_url', 'upc', 'name', 'description', 'price', 'quantity', 'category_name', 'category', 'created_at', 'updated_at']

    def get_images_url(self, obj):
        request = self.context.get('request')
        image = obj.images.first()
        if image and request is not None:
            return request.build_absolute_uri(image.image.url)
        return None



class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'





