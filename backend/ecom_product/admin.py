from django.contrib import admin

# Register your models here.
from .models import (
    ProductCategory,
    Product,
    ProductImage,
    Cart,
    CartItem,
    UserAddress,
    Payment,
    Wallet,
    Transaction,
    Vendor,
    Tender,
    TenderBid,
    RawProductList,
    RawProductListBatch,
    ReceivedOrder,
    FaultyItem,
    AcceptedProduct,
    VendorProductDetails
)

class VendorProductDetailsInline(admin.TabularInline):
    model = VendorProductDetails
    extra = 1

class VendorAdmin(admin.ModelAdmin):
    inlines = [VendorProductDetailsInline]

admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(UserAddress)
admin.site.register(Payment)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Tender)
admin.site.register(TenderBid)
admin.site.register(RawProductList)
admin.site.register(RawProductListBatch)
admin.site.register(ReceivedOrder)
admin.site.register(FaultyItem)
admin.site.register(AcceptedProduct)
admin.site.register(VendorProductDetails)