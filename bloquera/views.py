from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F, Sum
from decimal import Decimal
from .models import (
    ProductoBloquera, 
    MovimientoInventarioBloquera, 
    TipoMovimientoBloquera,
    OrdenProduccionBloquera,
    LoteProduccionBloquera
)
from .serializers import (
    ProductoBloqueraSerializer,
    ProductoBloqueraListSerializer,
    ProductosBloqueraStatsSerializer,
    MovimientoInventarioBloqueraSerializer,
    OrdenProduccionBloqueraSerializer,
    OrdenProduccionBloqueraListSerializer,
    LoteProduccionBloqueraSerializer
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

    def create(self, request, *args, **kwargs):
        """
        Sobrescribir create para agregar logging y mejor manejo de errores
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[ProductoBloquera] Creando producto. Datos recibidos: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"[ProductoBloquera] Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            self.perform_create(serializer)
            logger.info(f"[ProductoBloquera] Producto creado exitosamente: {serializer.data.get('codigo')}")
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"[ProductoBloquera] Error al crear producto: {str(e)}")
            return Response(
                {'error': f'Error al crear producto: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

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
        # Un producto tiene stock bajo cuando su stock actual es menor o igual al stock mínimo
        productos_stock_bajo = base_queryset.filter(
            stock_actual__lte=F('stock_minimo')
        ).count()
        
        # Stock total en unidades
        stock_total_unidades = base_queryset.aggregate(
            total=Sum('stock_actual')
        )['total'] or 0

        # Valor total del inventario (stock_actual * costo_produccion)
        # Calcular en Python para mayor precisión
        valor_total = Decimal('0.00')
        for producto in base_queryset.values('stock_actual', 'costo_produccion'):
            stock = producto.get('stock_actual') or 0
            costo = producto.get('costo_produccion') or Decimal('0.00')
            if isinstance(costo, (int, float)):
                costo = Decimal(str(costo))
            valor_total += Decimal(str(stock)) * costo

        stats = {
            'total_productos': total_productos,
            'productos_activos': productos_activos,
            'productos_inactivos': productos_inactivos,
            'productos_stock_bajo': productos_stock_bajo,
            'stock_total_unidades': stock_total_unidades,
            'valor_total': float(valor_total),
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

    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo movimiento de inventario
        El usuario se asigna automáticamente desde el token JWT
        """
        # Verificar que el usuario esté autenticado
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Usuario no autenticado. Debes estar logueado para crear movimientos.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Log para debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'[MovimientoInventario] Creando movimiento para usuario: {request.user.id} ({request.user.username})')
        logger.info(f'[MovimientoInventario] Datos recibidos: {request.data}')
        
        # Usar el método create del padre, que pasará el request al serializer
        return super().create(request, *args, **kwargs)

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


class OrdenProduccionBloqueraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para órdenes de producción de bloquera
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (eliminar)
    """
    queryset = OrdenProduccionBloquera.objects.select_related('producto').prefetch_related('lotes_produccion').all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilitar paginación, el frontend la maneja

    def get_serializer_class(self):
        if self.action == 'list':
            return OrdenProduccionBloqueraListSerializer
        return OrdenProduccionBloqueraSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por código, producto o supervisor
        - estado: PENDIENTE, EN_PROCESO, COMPLETADA, CANCELADA o 'todos'
        - producto: ID del producto
        """
        queryset = self.queryset

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |
                Q(producto__nombre__icontains=search) |
                Q(producto__codigo__icontains=search) |
                Q(supervisor__icontains=search)
            )

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado != 'todos':
            queryset = queryset.filter(estado=estado)

        # Filtro por producto
        producto_id = self.request.query_params.get('producto', None)
        if producto_id:
            try:
                queryset = queryset.filter(producto_id=int(producto_id))
            except ValueError:
                pass

        return queryset.order_by('-fecha_inicio', '-created_at')


class LoteProduccionBloqueraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para lotes de producción de bloquera
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (eliminar)
    """
    queryset = LoteProduccionBloquera.objects.select_related('orden', 'orden__producto').all()
    serializer_class = LoteProduccionBloqueraSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """
        Filtros opcionales:
        - orden: ID de la orden de producción
        """
        queryset = self.queryset

        # Filtro por orden
        orden_id = self.request.query_params.get('orden', None)
        if orden_id:
            try:
                queryset = queryset.filter(orden_id=int(orden_id))
            except ValueError:
                pass

        return queryset.order_by('-fecha_lote', '-hora_inicio')

    def perform_create(self, serializer):
        """
        Crear lote y pasar el usuario al contexto para el movimiento de inventario
        """
        # Pasar el usuario al contexto para que el modelo pueda usarlo al crear el movimiento
        instance = serializer.save()
        # El modelo ya maneja la creación del movimiento de inventario en su método save()
        # pero necesitamos asegurarnos de que tenga acceso al usuario
        if hasattr(instance, '_usuario_context'):
            instance._usuario_context = self.request.user
        else:
            # Si el modelo no tiene el atributo, intentar pasarlo de otra manera
            # Por ahora, el modelo usa usuario_id=1 como fallback, pero podemos mejorarlo
            pass
