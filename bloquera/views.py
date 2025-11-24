from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F, Sum
from .models import ProductoBloquera, MovimientoInventarioBloquera, TipoMovimientoBloquera
from .serializers import (
    ProductoBloqueraSerializer,
    ProductoBloqueraListSerializer,
    ProductosBloqueraStatsSerializer,
    MovimientoInventarioBloqueraSerializer
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


class MovimientoInventarioBloqueraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para movimientos de inventario de bloquera
    Permite GET (listar), POST (crear), GET/{id} (detalle)
    Los movimientos no se pueden editar ni eliminar (solo lectura después de creados)
    """
    queryset = MovimientoInventarioBloquera.objects.select_related('producto', 'usuario').all()
    serializer_class = MovimientoInventarioBloqueraSerializer
    permission_classes = [IsAuthenticated]
    # La paginación se maneja automáticamente con la configuración global (PAGE_SIZE: 20)

    def get_queryset(self):
        """
        Filtros opcionales:
        - producto: ID del producto
        - tipo: tipo de movimiento (ENTRADA, SALIDA, AJUSTE, etc.)
        - fecha_desde: fecha desde (YYYY-MM-DD)
        - fecha_hasta: fecha hasta (YYYY-MM-DD)
        """
        queryset = self.queryset

        # Filtro por producto
        producto_id = self.request.query_params.get('producto', None)
        if producto_id:
            try:
                queryset = queryset.filter(producto_id=int(producto_id))
            except ValueError:
                pass

        # Filtro por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            from django.utils.dateparse import parse_date
            fecha = parse_date(fecha_desde)
            if fecha:
                from django.utils import timezone
                queryset = queryset.filter(fecha_movimiento__date__gte=fecha)
        if fecha_hasta:
            from django.utils.dateparse import parse_date
            fecha = parse_date(fecha_hasta)
            if fecha:
                from django.utils import timezone
                queryset = queryset.filter(fecha_movimiento__date__lte=fecha)

        return queryset

    def update(self, request, *args, **kwargs):
        """
        Los movimientos no se pueden editar después de creados
        """
        return Response(
            {'error': 'Los movimientos de inventario no se pueden editar'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        """
        Los movimientos no se pueden eliminar después de creados
        """
        return Response(
            {'error': 'Los movimientos de inventario no se pueden eliminar'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=False, methods=['get'])
    def tipos(self, request):
        """
        Endpoint para obtener los tipos de movimiento disponibles
        """
        tipos = [
            {'value': choice[0], 'label': choice[1]}
            for choice in TipoMovimientoBloquera.choices
        ]
        return Response(tipos)
