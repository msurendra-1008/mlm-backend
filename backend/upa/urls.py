from rest_framework.routers import DefaultRouter
from .viewset import UPAUserViewSet

router = DefaultRouter()
router.register(r'upausers', UPAUserViewSet, basename='upausers')

urlpatterns = [
    # Other URL patterns...
]

urlpatterns += router.urls