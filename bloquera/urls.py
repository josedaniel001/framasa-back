from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoBloqueraViewSet, 
    MovimientoInventarioBloqueraViewSet,
    OrdenProduccionBloqueraViewSet,
    LoteProduccionBloqueraViewSet
)

router = DefaultRouter()
router.register(r'productos', ProductoBloqueraViewSet, basename='producto-bloquera')
router.register(r'movimientos-inventario', MovimientoInventarioBloqueraViewSet, basename='movimiento-inventario-bloquera')
router.register(r'ordenes-produccion', OrdenProduccionBloqueraViewSet, basename='orden-produccion-bloquera')
router.register(r'lotes-produccion', LoteProduccionBloqueraViewSet, basename='lote-produccion-bloquera')

urlpatterns = [
    path('', include(router.urls)),
]

