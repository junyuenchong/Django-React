from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.items.views import ItemViewSet

router = DefaultRouter()
# Register CRUD endpoints for Item resources.
router.register(r"items", ItemViewSet, basename="item")

urlpatterns = [
    path("", include(router.urls)),
]

