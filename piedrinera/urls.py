from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgregadoPiedrineraViewSet, CamionViewSet, MovimientoInventarioPiedrineraViewSet

router = DefaultRouter()
router.register(r'productos', AgregadoPiedrineraViewSet, basename='agregado-piedrinera')
router.register(r'camiones', CamionViewSet, basename='camion')
router.register(r'movimientos-inventario', MovimientoInventarioPiedrineraViewSet, basename='movimiento-inventario-piedrinera')

urlpatterns = [
    path('', include(router.urls)),
]

