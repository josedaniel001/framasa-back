from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F, Sum
from .models import ProductoBloquera
from .serializers import (
    ProductoBloqueraSerializer,
    ProductoBloqueraListSerializer,
    ProductosBloqueraStatsSerializer
)


class ProductoBloqueraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para productos de bloquera con filtros y estadísticas
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (desactivar)
    """
    queryset = ProductoBloquera.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilitar paginación, el frontend la maneja

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoBloqueraListSerializer
        return ProductoBloqueraSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por código, nombre, tipo_bloque o dimensiones
        - estado: 'activo', 'inactivo' o 'todos'
        - stock_minimo: 'bajo', 'suficiente' o 'todos'
        """
        queryset = self.queryset

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |
                Q(nombre__icontains=search) |
                Q(tipo_bloque__icontains=search) |
                Q(dimensiones__icontains=search)
            )

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado == 'activo':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivo':
            queryset = queryset.filter(activo=False)

        # Filtro por stock mínimo
        stock_minimo = self.request.query_params.get('stockMinimo', 'todos')
        if stock_minimo == 'bajo':
            queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))
        elif stock_minimo == 'suficiente':
            queryset = queryset.filter(stock_actual__gt=F('stock_minimo'))

        return queryset.order_by('codigo')

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: en lugar de eliminar el producto, solo lo desactiva
        """
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para obtener estadísticas de productos de bloquera
        Calcula estadísticas sobre TODOS los productos, sin filtros
        """
        # Usar el queryset base sin filtros para las estadísticas
        base_queryset = ProductoBloquera.objects.all()

        total_productos = base_queryset.count()
        productos_activos = base_queryset.filter(activo=True).count()
        productos_inactivos = base_queryset.filter(activo=False).count()
        
        # Productos con stock bajo (stock_actual <= stock_minimo)
        productos_stock_bajo = base_queryset.filter(
            stock_actual__lte=F('stock_minimo')
        ).count()
        
        # Stock total en unidades
        stock_total_unidades = base_queryset.aggregate(
            total=Sum('stock_actual')
        )['total'] or 0

        stats = {
            'total_productos': total_productos,
            'productos_activos': productos_activos,
            'productos_inactivos': productos_inactivos,
            'productos_stock_bajo': productos_stock_bajo,
            'stock_total_unidades': stock_total_unidades,
        }

        serializer = ProductosBloqueraStatsSerializer(stats)
        return Response(serializer.data)
