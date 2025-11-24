from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F
from .models import AgregadoPiedrinera, Camion, MovimientoInventarioPiedrinera, TipoMovimientoPiedrinera
from .serializers import (
    AgregadoPiedrineraSerializer,
    AgregadoPiedrineraListSerializer,
    AgregadosStatsSerializer,
    CamionSerializer,
    CamionListSerializer,
    MovimientoInventarioPiedrineraSerializer
)


class AgregadoPiedrineraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para agregados de piedrinera con filtros y estadísticas
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (eliminar)
    """
    queryset = AgregadoPiedrinera.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilitar paginación, el frontend la maneja

    def get_serializer_class(self):
        if self.action == 'list':
            return AgregadoPiedrineraListSerializer
        return AgregadoPiedrineraSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por código, nombre, tipo o proveedor
        - estado: 'activo', 'inactivo' o 'todos'
        - tipo: tipo de agregado o 'todos'
        - stock_minimo: 'bajo', 'suficiente' o 'todos'
        """
        queryset = self.queryset

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |
                Q(nombre__icontains=search) |
                Q(tipo__icontains=search) |
                Q(proveedor__icontains=search)
            )

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado == 'activo':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivo':
            queryset = queryset.filter(activo=False)

        # Filtro por tipo
        tipo = self.request.query_params.get('tipo', 'todos')
        if tipo != 'todos':
            queryset = queryset.filter(tipo=tipo)

        # Filtro por stock mínimo
        stock_minimo = self.request.query_params.get('stockMinimo', 'todos')
        if stock_minimo == 'bajo':
            queryset = queryset.filter(stock_actual_m3__lte=F('stock_minimo_m3'))
        elif stock_minimo == 'suficiente':
            queryset = queryset.filter(stock_actual_m3__gt=F('stock_minimo_m3'))

        return queryset.order_by('codigo')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para obtener estadísticas de agregados
        Calcula estadísticas sobre TODOS los agregados, sin filtros
        """
        base_queryset = AgregadoPiedrinera.objects.all()

        total_agregados = base_queryset.count()
        agregados_activos = base_queryset.filter(activo=True).count()
        agregados_inactivos = base_queryset.filter(activo=False).count()
        
        # Agregados con stock bajo (stock_actual_m3 <= stock_minimo_m3)
        agregados_stock_bajo = base_queryset.filter(
            stock_actual_m3__lte=F('stock_minimo_m3')
        ).count()

        stats = {
            'total_agregados': total_agregados,
            'agregados_activos': agregados_activos,
            'agregados_inactivos': agregados_inactivos,
            'agregados_stock_bajo': agregados_stock_bajo,
        }

        serializer = AgregadosStatsSerializer(stats)
        return Response(serializer.data)


class CamionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para camiones con filtros
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (eliminar)
    """
    queryset = Camion.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilitar paginación, el frontend la maneja

    def get_serializer_class(self):
        if self.action == 'list':
            return CamionListSerializer
        return CamionSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por placa, marca o modelo
        - estado: estado del camión o 'todos'
        - activo: 'activo', 'inactivo' o 'todos'
        """
        queryset = self.queryset

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(placa__icontains=search) |
                Q(marca__icontains=search) |
                Q(modelo__icontains=search)
            )

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado != 'todos':
            queryset = queryset.filter(estado_actual=estado)

        # Filtro por activo
        activo = self.request.query_params.get('activo', 'todos')
        if activo == 'activo':
            queryset = queryset.filter(activo=True)
        elif activo == 'inactivo':
            queryset = queryset.filter(activo=False)

        return queryset.order_by('placa')


class MovimientoInventarioPiedrineraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para movimientos de inventario de piedrinera
    Permite GET (listar), POST (crear), GET/{id} (detalle)
    Los movimientos no se pueden editar ni eliminar (solo lectura después de creados)
    """
    queryset = MovimientoInventarioPiedrinera.objects.select_related('producto', 'usuario').all()
    serializer_class = MovimientoInventarioPiedrineraSerializer
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
            for choice in TipoMovimientoPiedrinera.choices
        ]
        return Response(tipos)
