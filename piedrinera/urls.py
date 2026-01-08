from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgregadoPiedrineraViewSet, CamionViewSet, MovimientoInventarioPiedrineraViewSet, ProduccionPiedrineraViewSet

router = DefaultRouter()
router.register(r'productos', AgregadoPiedrineraViewSet, basename='agregado-piedrinera')
router.register(r'camiones', CamionViewSet, basename='camion')
router.register(r'movimientos-inventario', MovimientoInventarioPiedrineraViewSet, basename='movimiento-inventario-piedrinera')
router.register(r'produccion', ProduccionPiedrineraViewSet, basename='produccion-piedrinera')

urlpatterns = [
    path('', include(router.urls)),
]

