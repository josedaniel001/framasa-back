from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoBloqueraViewSet

router = DefaultRouter()
router.register(r'productos', ProductoBloqueraViewSet, basename='producto-bloquera')

urlpatterns = [
    path('', include(router.urls)),
]

