from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacturaViewSet, PagoViewSet, CotizacionViewSet

router = DefaultRouter()
router.register(r'facturas', FacturaViewSet, basename='factura')
router.register(r'pagos', PagoViewSet, basename='pago')
router.register(r'cotizaciones', CotizacionViewSet, basename='cotizacion')

urlpatterns = [
    path('', include(router.urls)),
]

