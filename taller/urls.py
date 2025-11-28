# URLs del módulo Taller

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaquinariaViewSet

router = DefaultRouter()
router.register(r'maquinaria', MaquinariaViewSet, basename='maquinaria')

urlpatterns = [
    path('', include(router.urls)),
]
