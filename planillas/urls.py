from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmpleadoViewSet,
    AsistenciaViewSet,
    NominaViewSet,
    NominaDetalleViewSet,
    PagoNominaViewSet,
    CargoViewSet
)

router = DefaultRouter()
router.register(r'empleados', EmpleadoViewSet, basename='empleado')
router.register(r'asistencias', AsistenciaViewSet, basename='asistencia')
router.register(r'nominas', NominaViewSet, basename='nomina')
router.register(r'nominas-detalle', NominaDetalleViewSet, basename='nomina-detalle')
router.register(r'pagos-nomina', PagoNominaViewSet, basename='pago-nomina')
router.register(r'cargos', CargoViewSet, basename='cargo')

urlpatterns = [
    path('', include(router.urls)),
]
