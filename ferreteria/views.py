from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Case, When, IntegerField, F
from .models import Producto, CategoriaProducto, UnidadMedida, Cliente, Proveedor, MovimientoInventario
from .serializers import (
    ProductoSerializer,
    ProductoListSerializer,
    CategoriaProductoSerializer,
    UnidadMedidaSerializer,
    ProductosStatsSerializer,
    ClienteSerializer,
    ProveedorSerializer,
    MovimientoInventarioSerializer
)


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para productos con filtros y estadísticas
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (eliminar)
    """
    queryset = Producto.objects.select_related('categoria', 'unidad_medida', 'proveedor').all()
    permission_classes = [IsAuthenticated]
    # La paginación se maneja automáticamente con la configuración global (PAGE_SIZE: 20)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por código, nombre o categoría
        - estado: 'activo', 'inactivo' o 'todos'
        - categoria: ID de categoría o 'todas'
        - stock_minimo: 'bajo', 'suficiente' o 'todos'
        """
        queryset = self.queryset

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |
                Q(nombre__icontains=search) |
                Q(categoria__nombre__icontains=search)
            )

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado == 'activo':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivo':
            queryset = queryset.filter(activo=False)

        # Filtro por categoría
        categoria = self.request.query_params.get('categoria', 'todas')
        if categoria != 'todas':
            try:
                categoria_id = int(categoria)
                queryset = queryset.filter(categoria_id=categoria_id)
            except ValueError:
                # Si no es un número, buscar por nombre
                queryset = queryset.filter(categoria__nombre=categoria)

        # Filtro por stock mínimo
        stock_minimo = self.request.query_params.get('stockMinimo', 'todos')
        if stock_minimo == 'bajo':
            queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))
        elif stock_minimo == 'suficiente':
            queryset = queryset.filter(stock_actual__gt=F('stock_minimo'))

        return queryset.order_by('codigo')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para obtener estadísticas de productos
        Calcula estadísticas sobre TODOS los productos, sin filtros
        """
        # Usar el queryset base sin filtros para las estadísticas
        base_queryset = Producto.objects.all()

        total_productos = base_queryset.count()
        productos_activos = base_queryset.filter(activo=True).count()
        productos_inactivos = base_queryset.filter(activo=False).count()
        
        # Productos con stock bajo (stock_actual <= stock_minimo)
        productos_stock_bajo = base_queryset.filter(
            stock_actual__lte=F('stock_minimo')
        ).count()

        stats = {
            'total_productos': total_productos,
            'productos_activos': productos_activos,
            'productos_inactivos': productos_inactivos,
            'productos_stock_bajo': productos_stock_bajo,
        }

        serializer = ProductosStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def categorias(self, request):
        """
        Endpoint para obtener todas las categorías activas
        """
        categorias = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
        serializer = CategoriaProductoSerializer(categorias, many=True)
        return Response(serializer.data)


class CategoriaProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para categorías de productos
    """
    queryset = CategoriaProducto.objects.filter(activo=True)
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilitar paginación


class UnidadMedidaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para unidades de medida
    """
    queryset = UnidadMedida.objects.filter(activo=True)
    serializer_class = UnidadMedidaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilitar paginación


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para clientes con filtros y estadísticas
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (desactivar)
    Por defecto solo muestra clientes activos. El DELETE hace un soft delete (marca activo=False)
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    # La paginación se maneja automáticamente con la configuración global (PAGE_SIZE: 20)

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por nombre, NIT, teléfono o email
        - activo: 'true', 'false' o 'todos' (por defecto solo muestra activos)
        - periodo_registro: 'semana', 'mes', 'año' o 'todos'
        - tiene_compras: 'si', 'no' o 'todos'
        """
        queryset = self.queryset

        # Por defecto solo mostrar clientes activos
        activo = self.request.query_params.get('activo', 'true')
        if activo.lower() == 'true':
            queryset = queryset.filter(activo=True)
        elif activo.lower() == 'false':
            queryset = queryset.filter(activo=False)
        # Si es 'todos', no se filtra por activo

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(nit__icontains=search) |
                Q(telefono__icontains=search) |
                Q(email__icontains=search)
            )

        # Filtro por período de registro
        periodo_registro = self.request.query_params.get('periodo_registro', None)
        if periodo_registro:
            from django.utils import timezone
            from datetime import timedelta
            
            ahora = timezone.now()
            if periodo_registro == 'semana':
                semana_atras = ahora - timedelta(days=7)
                queryset = queryset.filter(fecha_registro__gte=semana_atras)
            elif periodo_registro == 'mes':
                mes_atras = ahora - timedelta(days=30)
                queryset = queryset.filter(fecha_registro__gte=mes_atras)
            elif periodo_registro == 'año':
                año_atras = ahora - timedelta(days=365)
                queryset = queryset.filter(fecha_registro__gte=año_atras)

        return queryset.order_by('nombre')

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: en lugar de eliminar el cliente, solo lo desactiva
        """
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para obtener estadísticas de clientes
        Solo cuenta clientes activos por defecto
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Sum
        
        # Solo contar clientes activos
        base_queryset = Cliente.objects.filter(activo=True)
        ahora = timezone.now()
        mes_atras = ahora - timedelta(days=30)

        total_clientes = base_queryset.count()
        nuevos_clientes_mes = base_queryset.filter(
            fecha_registro__gte=mes_atras
        ).count()

        # Nota: Estas estadísticas requerirían relaciones con ventas/facturas
        # Por ahora las dejamos en 0 hasta que se implementen esas relaciones
        stats = {
            'total_clientes': total_clientes,
            'clientes_con_compras': 0,  # Se calculará cuando haya relación con ventas
            'clientes_con_compras_recientes': 0,  # Se calculará cuando haya relación con ventas
            'nuevos_clientes_mes': nuevos_clientes_mes,
            'valor_total_compras': 0,  # Se calculará cuando haya relación con ventas
            'promedio_compras_por_cliente': 0,  # Se calculará cuando haya relación con ventas
            'total_cotizaciones': 0,  # Se calculará cuando haya relación con cotizaciones
            'total_facturas': 0,  # Se calculará cuando haya relación con facturas
        }

        return Response(stats)


class ProveedorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para proveedores con filtros y estadísticas
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (desactivar)
    Por defecto solo muestra proveedores activos. El DELETE hace un soft delete (marca activo=False)
    """
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]
    # La paginación se maneja automáticamente con la configuración global (PAGE_SIZE: 20)

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por nombre, NIT, teléfono o email
        - activo: 'true', 'false' o 'todos' (por defecto solo muestra activos)
        - periodo_registro: 'semana', 'mes', 'año' o 'todos'
        """
        queryset = self.queryset

        # Por defecto solo mostrar proveedores activos
        activo = self.request.query_params.get('activo', 'true')
        if activo.lower() == 'true':
            queryset = queryset.filter(activo=True)
        elif activo.lower() == 'false':
            queryset = queryset.filter(activo=False)
        # Si es 'todos', no se filtra por activo

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(nit__icontains=search) |
                Q(telefono__icontains=search) |
                Q(email__icontains=search) |
                Q(contacto__icontains=search)
            )

        # Filtro por período de registro
        periodo_registro = self.request.query_params.get('periodo_registro', None)
        if periodo_registro:
            from django.utils import timezone
            from datetime import timedelta
            
            ahora = timezone.now()
            if periodo_registro == 'semana':
                semana_atras = ahora - timedelta(days=7)
                queryset = queryset.filter(fecha_registro__gte=semana_atras)
            elif periodo_registro == 'mes':
                mes_atras = ahora - timedelta(days=30)
                queryset = queryset.filter(fecha_registro__gte=mes_atras)
            elif periodo_registro == 'año':
                año_atras = ahora - timedelta(days=365)
                queryset = queryset.filter(fecha_registro__gte=año_atras)

        return queryset.order_by('nombre')

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: en lugar de eliminar el proveedor, solo lo desactiva
        """
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para obtener estadísticas de proveedores
        Solo cuenta proveedores activos por defecto
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Solo contar proveedores activos
        base_queryset = Proveedor.objects.filter(activo=True)
        ahora = timezone.now()
        mes_atras = ahora - timedelta(days=30)

        total_proveedores = base_queryset.count()
        nuevos_proveedores_mes = base_queryset.filter(
            fecha_registro__gte=mes_atras
        ).count()

        # Nota: Estas estadísticas requerirían relaciones con productos/compras
        stats = {
            'total_proveedores': total_proveedores,
            'nuevos_proveedores_mes': nuevos_proveedores_mes,
            'proveedores_con_productos': Proveedor.objects.filter(
                productos__isnull=False
            ).distinct().count(),
        }

        return Response(stats)


class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para movimientos de inventario
    Permite GET (listar), POST (crear), GET/{id} (detalle)
    Los movimientos no se pueden editar ni eliminar (solo lectura después de creados)
    """
    queryset = MovimientoInventario.objects.select_related('producto', 'usuario').all()
    serializer_class = MovimientoInventarioSerializer
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
        from .models import TipoMovimiento
        tipos = [
            {'value': choice[0], 'label': choice[1]}
            for choice in TipoMovimiento.choices
        ]
        return Response(tipos)
