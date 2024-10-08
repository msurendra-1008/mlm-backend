

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewset import LegIncomeModelViewSet, UserViewSet, PublicViewSet
from .helpers import ProtectedView, PublicView



router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'public', PublicViewSet, basename='public')
router.register(r'leg-income', LegIncomeModelViewSet, basename='leg-income')

urlpatterns = [
    path('', include(router.urls)),
    # path('protected/', ProtectedView.as_view(), name='protected'),
    # path('public/', PublicView.as_view(), name='public')
]
