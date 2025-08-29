from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .viewsets import *


router = DefaultRouter()
router.register(r'product-categories', ProductCategoryViewSet, basename='product-category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-images', ProductImageViewSet, basename='product-image')
# router.register(r'user-addresses', UserAddressViewSet, basename='user-address')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'payment', PaymentViewSet, basename='payment')
router.register(r'user-address', UserAddressViewSet, basename='user-address')
router.register(r'wallet', WalletViewSet,basename='wallet')
router.register(r'transactions', TransactionViewSet,basename='transaction')
router.register(r'vendors', VendorViewSet, basename='vendors')
router.register(r'tenders', TenderViewSet, basename='tenders')
router.register(r'tender-bids', TenderBidViewSet, basename='tender-bids')
router.register(r'awarded-tender', TenderBidPreRequsitViewSet, basename='awarded-tender')
router.register(r'raw-product-list', RawProductListViewSet, basename='raw-product-list')
router.register(r'received-orders', ReceivedOrderViewSet, basename='received-orders')
router.register(r'faulty-items', FaultyItemViewSet, basename='faulty-items')
router.register(r'accepted-products', AcceptedProductViewSet, basename='accepted-products')
router.register(r'vendor-product-details', VendorProductDetailsViewSet, basename='vendor-product-details')
# router.register(r'cart-items', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('open-tenders/', OpenTendersView.as_view(), name='open-tenders'),
    path('ecom-product/', include(router.urls)),
]

