# URLs del módulo Taller

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaquinariaViewSet, OrdenTrabajoViewSet

router = DefaultRouter()
router.register(r'maquinaria', MaquinariaViewSet, basename='maquinaria')
router.register(r'ordenes', OrdenTrabajoViewSet, basename='ordenes-trabajo')

urlpatterns = [
    path('', include(router.urls)),
]
