from django.contrib import admin

# Register your models here.
from .models import ( 
    ProductCategory,
    Product,
    ProductImage,
    Cart, 
    CartItem, 
    UserAddress , 
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
    AcceptedProduct
)

admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(UserAddress)
admin.site.register(Payment)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Vendor)
admin.site.register(Tender)
admin.site.register(TenderBid)
admin.site.register(RawProductList)
admin.site.register(RawProductListBatch)
admin.site.register(ReceivedOrder)
admin.site.register(FaultyItem)
admin.site.register(AcceptedProduct)