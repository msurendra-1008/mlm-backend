

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewset import LegIncomeModelViewSet, UserViewSet, PublicViewSet, IncomeSettingViewSet, IncomeSettingForWomenOldViewSet, CustomUserTreeViewSet
from .helpers import ProtectedView, PublicView

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'public', PublicViewSet, basename='public')
router.register(r'leg-income', LegIncomeModelViewSet, basename='leg-income')
router.register(r'general-income', IncomeSettingViewSet, basename='general-income')
router.register(r'women-income', IncomeSettingForWomenOldViewSet, basename='women-income')
router.register(r'users-with-legs', CustomUserTreeViewSet, basename='user-tree')

urlpatterns = [
    path('', include(router.urls)),
    # path('protected/', ProtectedView.as_view(), name='protected'),
    # path('public/', PublicView.as_view(), name='public')
]
