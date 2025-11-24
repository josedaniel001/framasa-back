from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CategoriaProductoViewSet, UnidadMedidaViewSet, ClienteViewSet, ProveedorViewSet, MovimientoInventarioViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'categorias', CategoriaProductoViewSet, basename='categoria')
router.register(r'unidades-medida', UnidadMedidaViewSet, basename='unidad-medida')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'movimientos-inventario', MovimientoInventarioViewSet, basename='movimiento-inventario')

urlpatterns = [
    path('', include(router.urls)),
]

