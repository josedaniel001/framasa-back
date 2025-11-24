from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoBloqueraViewSet, MovimientoInventarioBloqueraViewSet

router = DefaultRouter()
router.register(r'productos', ProductoBloqueraViewSet, basename='producto-bloquera')
router.register(r'movimientos-inventario', MovimientoInventarioBloqueraViewSet, basename='movimiento-inventario-bloquera')

urlpatterns = [
    path('', include(router.urls)),
]

