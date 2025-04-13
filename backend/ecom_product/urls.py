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
# router.register(r'cart-items', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('ecom-product/', include(router.urls)),
]

