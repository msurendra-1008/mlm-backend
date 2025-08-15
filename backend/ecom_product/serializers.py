from django.conf import settings
from rest_framework import serializers
from .models import(
    Payment,
    ProductCategory,
    Product,
    ProductImage,
    Transaction,
    UserAddress,
    Cart,
    CartItem,
    Wallet,
    Vendor,
    Tender,
    TenderBid,
    RawProductList,
    RawProductListBatch,
    ReceivedOrder,
    FaultyItem,
    AcceptedProduct,
)


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'email', 'mobile', 'address', 'product', 'gst_number', 'created_at', 'is_approved']
        
        

class TenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = ['id', 'tender_product_no', 'title', 'description', 'deadline', 'location', 'budget', 'quantity', 'status', 'tender_date', 'created_at']
        
class TenderBidSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    tender_title = serializers.CharField(source='tender.title', read_only=True)

    class Meta:
        model = TenderBid
        fields = '__all__'
        read_only_fields = ['vendor', 'tender', 'submitted_at']


class RawProductListBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawProductListBatch
        fields = ['id', 'delivery_date', 'quantity']

class RawProductListSerializer(serializers.ModelSerializer):
    batches = RawProductListBatchSerializer(many=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    tender_title = serializers.CharField(source='tender.title', read_only=True)
    approved_batches_count = serializers.SerializerMethodField()

    class Meta:
        model = RawProductList
        fields = [
            'id', 'tender', 'vendor', 'tender_bid', 'status',
            'vendor_name', 'tender_title', 'created_at', 'batches',
            'approved_batches_count'
        ]

    def get_approved_batches_count(self, obj):
        return obj.batches.count()

    def create(self, validated_data):
        batches_data = validated_data.pop('batches')
        raw_list = RawProductList.objects.create(**validated_data)
        for batch_data in batches_data:
            RawProductListBatch.objects.create(raw_list=raw_list, **batch_data)
        return raw_list

    def update(self, instance, validated_data):
        # Allow only status to be updated directly for now
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class ReceivedOrderSerializer(serializers.ModelSerializer):
    tender_title = serializers.CharField(source='tender.title', read_only=True)
    tender_product_no = serializers.CharField(source='tender.tender_product_no', read_only=True)

    class Meta:
        model = ReceivedOrder
        fields = [
            'id', 'vendor', 'tender', 'tender_title', 'tender_product_no', 
            'batch', 'received_quantity', 'received_at', 'inspection_status', 'updated_at'
        ]


class FaultyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaultyItem
        fields = [
            'id', 'received_order', 'description', 'faulty_quantity', 
            'reported_at', 'updated_at'
        ]


class AcceptedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcceptedProduct
        fields = [
            'id', 'received_order', 'description', 'accepted_quantity', 
            'accepted_at', 'updated_at'
        ]


    

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
    product = CartProductSerializer(many=True, read_only=True)
    product_id = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    total_price = serializers.SerializerMethodField()
    # user_address = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_id', 'quantity', 'total_price']

    def get_total_price(self, obj):
        # return obj.quantity * obj.product.price
        return sum(product.price * obj.quantity for product in obj.product.all())
    
    # def get_user_address(self, obj):
    #     if obj.user_address:
    #         return {
    #             "id": obj.user_address.id,
    #             "address": obj.user_address.address,
    #             "city": obj.user_address.city,
    #             "state": obj.user_address.state,
    #             "zip_code": obj.user_address.zip_code,
    #             "is_default": obj.user_address.is_default
    #         }
    #     return None
    
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'quantity', 'total_price', 'created_at', 'updated_at']

    def get_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_total_price(self, obj):
        total_price = 0
        for item in obj.items.all():
            for product in item.product.all():  # Handle the ManyToMany relationship
                total_price += item.quantity * product.price
        return total_price


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'cart_item', 'payment_id', 'order_amount', 'status', 'created_at']
        read_only_fields = ['created_at']

    def validate_cart_item(self, value):
        if value.is_payment:
            raise serializers.ValidationError("Payment already processed for this order")
        return value
    

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['user', 'balance']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'wallet', 'amount', 'transaction_type', 'created_at', 'description']


