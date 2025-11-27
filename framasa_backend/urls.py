"""
URL configuration for framasa_backend project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/ferreteria/', include('ferreteria.urls')),
    path('api/bloquera/', include('bloquera.urls')),
    path('api/piedrinera/', include('piedrinera.urls')),
    path('api/planillas/', include('planillas.urls')),
    path('api/reportes/', include('reportes.urls')),
    path('api/taller/', include('taller.urls')),
]

