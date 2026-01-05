from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovimientoCajaViewSet, MovimientoCajaDetalleViewSet

router = DefaultRouter()
router.register(r'movimientos', MovimientoCajaViewSet, basename='movimientos-caja')
router.register(r'detalles', MovimientoCajaDetalleViewSet, basename='detalles-caja')

urlpatterns = [
    path('', include(router.urls)),
]

