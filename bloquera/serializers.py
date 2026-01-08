from rest_framework import serializers
from .models import (
    ProductoBloquera, 
    MovimientoInventarioBloquera, 
    TipoMovimientoBloquera,
    OrdenProduccionBloquera,
    LoteProduccionBloquera
)


class ProductoBloqueraSerializer(serializers.ModelSerializer):
    """
    Serializer para productos de bloquera
    """
    # Campos calculados
    tiene_stock_bajo = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductoBloquera
        fields = (
            'id', 'codigo', 'nombre', 'descripcion',
            'tipo_bloque', 'dimensiones',
            'precio_unitario', 'precio_descuento', 'costo_produccion',
            'stock_actual', 'stock_minimo',
            'activo', 'tiene_stock_bajo',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        """
        Personalizar la representación para que coincida con el formato esperado por el frontend
        Incluye tanto los campos en snake_case como camelCase
        """
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'descripcion': data.get('descripcion', ''),
            'tipoBloque': data.get('tipo_bloque', ''),
            'dimensiones': data.get('dimensiones', ''),
            'precioVentaUnitario': float(data.get('precio_unitario', 0)),
            'precioDescuento': float(data.get('precio_descuento')) if data.get('precio_descuento') is not None else None,
            'costoProduccionUnitario': float(data.get('costo_produccion', 0)),
            'stockActual': data.get('stock_actual', 0),
            'stockMinimo': data.get('stock_minimo', 0),
            'activo': data.get('activo', False),
            'tieneStockBajo': data.get('tiene_stock_bajo', False),
            'fechaCreacion': data.get('created_at', ''),
            'ultimaActualizacion': data.get('updated_at', ''),
            # También incluir campos en snake_case para compatibilidad
            'tipo_bloque': data.get('tipo_bloque', ''),
            'precio_unitario': float(data.get('precio_unitario', 0)),
            'precio_descuento': float(data.get('precio_descuento')) if data.get('precio_descuento') is not None else None,
            'costo_produccion': float(data.get('costo_produccion', 0)),
            'stock_actual': data.get('stock_actual', 0),
            'stock_minimo': data.get('stock_minimo', 0),
        }


class ProductoBloqueraListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar productos de bloquera
    """
    class Meta:
        model = ProductoBloquera
        fields = (
            'id', 'codigo', 'nombre', 'tipo_bloque', 'dimensiones',
            'precio_unitario', 'precio_descuento', 'stock_actual', 'stock_minimo', 'activo'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'tipoBloque': data.get('tipo_bloque', ''),
            'dimensiones': data.get('dimensiones', ''),
            'precioVentaUnitario': float(data.get('precio_unitario', 0)),
            'precioDescuento': float(data.get('precio_descuento')) if data.get('precio_descuento') is not None else None,
            'stockActual': data.get('stock_actual', 0),
            'stockMinimo': data.get('stock_minimo', 0),
            'stock_minimo': data.get('stock_minimo', 0),  # Incluir también en snake_case para compatibilidad
            'activo': data.get('activo', False),
        }


class ProductosBloqueraStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de productos de bloquera
    """
    total_productos = serializers.IntegerField()
    productos_activos = serializers.IntegerField()
    productos_inactivos = serializers.IntegerField()
    productos_stock_bajo = serializers.IntegerField()
    stock_total_unidades = serializers.IntegerField()
    valor_total = serializers.FloatField()


class MovimientoInventarioBloqueraSerializer(serializers.ModelSerializer):
    """
    Serializer para movimientos de inventario de bloquera
    """
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = MovimientoInventarioBloquera
        fields = (
            'id', 'producto', 'producto_id', 'producto_codigo', 'producto_nombre',
            'tipo', 'tipo_display', 'cantidad',
            'stock_anterior', 'stock_nuevo',
            'motivo', 'observaciones',
            'usuario', 'usuario_id', 'usuario_nombre',
            'fecha_movimiento', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'stock_anterior', 'stock_nuevo', 'fecha_movimiento',
            'created_at', 'updated_at', 'producto_codigo', 'producto_nombre',
            'usuario', 'usuario_id', 'usuario_nombre', 'tipo_display'
        )

    def validate(self, data):
        """
        Validación personalizada
        """
        tipo = data.get('tipo')
        cantidad = data.get('cantidad')
        producto = data.get('producto')

        # Obtener la instancia del producto si es necesario
        producto_instance = producto
        # Verificar si producto es una instancia del modelo o solo un ID
        if producto and not isinstance(producto, ProductoBloquera):
            # Si producto es solo un ID (número o string), obtener la instancia
            try:
                producto_instance = ProductoBloquera.objects.get(pk=producto)
            except (ProductoBloquera.DoesNotExist, ValueError, TypeError) as e:
                raise serializers.ValidationError({
                    'producto': 'El producto especificado no existe'
                })

        # Para ENTRADA, SALIDA, DEVOLUCION, TRANSFERENCIA: cantidad debe ser positiva
        if tipo in [TipoMovimientoBloquera.ENTRADA, TipoMovimientoBloquera.SALIDA,
                    TipoMovimientoBloquera.DEVOLUCION, TipoMovimientoBloquera.TRANSFERENCIA]:
            if cantidad <= 0:
                raise serializers.ValidationError({
                    'cantidad': 'La cantidad debe ser mayor a 0 para este tipo de movimiento'
                })

        # Para SALIDA y TRANSFERENCIA: verificar que haya stock suficiente
        if tipo in [TipoMovimientoBloquera.SALIDA, TipoMovimientoBloquera.TRANSFERENCIA]:
            if producto_instance and producto_instance.stock_actual < cantidad:
                raise serializers.ValidationError({
                    'cantidad': f'Stock insuficiente. Stock actual: {producto_instance.stock_actual}'
                })

        # Actualizar data con la instancia del producto si fue necesario obtenerla
        if producto_instance and not isinstance(producto, ProductoBloquera):
            data['producto'] = producto_instance

        return data

    def create(self, validated_data):
        """
        Crear movimiento y asignar usuario automáticamente desde el token JWT
        El usuario debe ser el que está autenticado (el que tiene el token)
        """
        # Obtener el usuario del request (viene del token JWT)
        request = self.context.get('request')
        
        if not request:
            raise serializers.ValidationError({
                'usuario': 'No se pudo obtener el request. Error interno del servidor.'
            })
        
        if not hasattr(request, 'user'):
            raise serializers.ValidationError({
                'usuario': 'El request no tiene información de usuario. Verifica la autenticación.'
            })
        
        if not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError({
                'usuario': 'Usuario no autenticado. Debes estar logueado para crear movimientos.'
            })
        
        # Asignar el usuario autenticado (el que tiene el token JWT)
        validated_data['usuario'] = request.user
        
        # Log para debugging (solo en desarrollo)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'Creando movimiento de inventario para usuario: {request.user.id} ({request.user.username})')
        
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Personalizar la representación para el frontend
        """
        data = super().to_representation(instance)
        return {
            'id': data.get('id'),
            'producto': {
                'id': instance.producto_id,
                'codigo': data.get('producto_codigo'),
                'nombre': data.get('producto_nombre'),
            },
            'producto_id': instance.producto_id,
            'tipo': data.get('tipo'),
            'tipoDisplay': data.get('tipo_display'),
            'cantidad': data.get('cantidad'),
            'stockAnterior': data.get('stock_anterior'),
            'stockNuevo': data.get('stock_nuevo'),
            'motivo': data.get('motivo'),
            'observaciones': data.get('observaciones'),
            'usuario': {
                'id': instance.usuario_id,
                'nombre': data.get('usuario_nombre'),
            },
            'usuario_id': instance.usuario_id,
            'fechaMovimiento': data.get('fecha_movimiento'),
            'fecha_movimiento': data.get('fecha_movimiento'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at'),
        }


class LoteProduccionBloqueraSerializer(serializers.ModelSerializer):
    """
    Serializer para lotes de producción de bloquera
    """
    orden_codigo = serializers.CharField(source='orden.codigo', read_only=True)
    calidad_display = serializers.CharField(source='get_calidad_display', read_only=True)

    class Meta:
        model = LoteProduccionBloquera
        fields = (
            'id', 'orden', 'orden_codigo',
            'fecha_lote', 'hora_inicio', 'hora_fin',
            'cantidad_producida', 'cantidad_defectuosa',
            'calidad', 'calidad_display',
            'supervisor', 'notas',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'orden_codigo', 'calidad_display')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id')),
            'ordenId': instance.orden.id,
            'ordenCodigo': data.get('orden_codigo'),
            'fechaProduccion': data.get('fecha_lote'),
            'fecha_lote': data.get('fecha_lote'),
            'horaInicio': data.get('hora_inicio'),
            'hora_inicio': data.get('hora_inicio'),
            'horaFin': data.get('hora_fin'),
            'hora_fin': data.get('hora_fin'),
            'cantidadProducida': data.get('cantidad_producida'),
            'cantidad_producida': data.get('cantidad_producida'),
            'cantidadDefectuosa': data.get('cantidad_defectuosa'),
            'cantidad_defectuosa': data.get('cantidad_defectuosa'),
            'calidad': data.get('calidad'),
            'calidadDisplay': data.get('calidad_display'),
            'supervisor': data.get('supervisor'),
            'notas': data.get('notas'),
            'createdAt': data.get('created_at'),
            'updatedAt': data.get('updated_at'),
        }


class OrdenProduccionBloqueraSerializer(serializers.ModelSerializer):
    """
    Serializer para órdenes de producción de bloquera (detalle completo)
    """
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cantidad_producida_total = serializers.IntegerField(read_only=True)
    cantidad_pendiente = serializers.IntegerField(read_only=True)
    progreso_porcentaje = serializers.FloatField(read_only=True)
    esta_completada = serializers.BooleanField(read_only=True)
    esta_vencida = serializers.BooleanField(read_only=True)
    lotes_produccion = LoteProduccionBloqueraSerializer(many=True, read_only=True)

    class Meta:
        model = OrdenProduccionBloquera
        fields = (
            'id', 'codigo', 'producto', 'producto_id', 'producto_nombre', 'producto_codigo',
            'cantidad_solicitada', 'fecha_inicio', 'fecha_fin_estimada',
            'supervisor', 'notas', 'estado', 'estado_display',
            'cantidad_producida_total', 'cantidad_pendiente', 'progreso_porcentaje',
            'esta_completada', 'esta_vencida',
            'lotes_produccion',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'codigo', 'created_at', 'updated_at',
            'producto_nombre', 'producto_codigo', 'estado_display',
            'cantidad_producida_total', 'cantidad_pendiente', 'progreso_porcentaje',
            'esta_completada', 'esta_vencida', 'lotes_produccion'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id')),
            'codigo': data.get('codigo'),
            'productoId': instance.producto.id,
            'producto_id': instance.producto.id,
            'nombreProducto': data.get('producto_nombre'),
            'productoCodigo': data.get('producto_codigo'),
            'cantidadSolicitada': data.get('cantidad_solicitada'),
            'cantidad_solicitada': data.get('cantidad_solicitada'),
            'cantidadProducida': data.get('cantidad_producida_total'),
            'cantidad_producida_total': data.get('cantidad_producida_total'),
            'fechaInicio': data.get('fecha_inicio'),
            'fecha_inicio': data.get('fecha_inicio'),
            'fechaFinEstimada': data.get('fecha_fin_estimada'),
            'fecha_fin_estimada': data.get('fecha_fin_estimada'),
            'fechaCreacion': data.get('created_at'),
            'responsable': data.get('supervisor'),
            'supervisor': data.get('supervisor'),
            'notas': data.get('notas'),
            'estado': data.get('estado'),
            'estadoDisplay': data.get('estado_display'),
            'lotes': data.get('lotes_produccion', []),
            'lotes_produccion': data.get('lotes_produccion', []),
            'progreso': data.get('progreso_porcentaje', 0),
            'createdAt': data.get('created_at'),
            'updatedAt': data.get('updated_at'),
        }

    def create(self, validated_data):
        """
        Crear orden y generar código automáticamente si no se proporciona
        """
        if 'codigo' not in validated_data or not validated_data['codigo']:
            from datetime import date
            año = date.today().year
            ultimo = OrdenProduccionBloquera.objects.filter(
                codigo__startswith=f'OP-{año}-'
            ).order_by('-codigo').first()
            
            if ultimo:
                try:
                    ultimo_numero = int(ultimo.codigo.split('-')[-1])
                    nuevo_numero = ultimo_numero + 1
                except:
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            validated_data['codigo'] = f'OP-{año}-{nuevo_numero:04d}'
        
        return super().create(validated_data)


class OrdenProduccionBloqueraListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar órdenes de producción
    """
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cantidad_producida_total = serializers.IntegerField(read_only=True)
    progreso_porcentaje = serializers.FloatField(read_only=True)

    class Meta:
        model = OrdenProduccionBloquera
        fields = (
            'id', 'codigo', 'producto_id', 'producto_nombre', 'producto_codigo',
            'cantidad_solicitada', 'cantidad_producida_total', 'progreso_porcentaje',
            'fecha_inicio', 'fecha_fin_estimada', 'estado', 'estado_display',
            'supervisor', 'created_at'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id')),
            'codigo': data.get('codigo'),
            'productoId': data.get('producto_id'),
            'nombreProducto': data.get('producto_nombre'),
            'productoCodigo': data.get('producto_codigo'),
            'cantidadSolicitada': data.get('cantidad_solicitada'),
            'cantidadProducida': data.get('cantidad_producida_total', 0),
            'fechaInicio': data.get('fecha_inicio'),
            'fechaFinEstimada': data.get('fecha_fin_estimada'),
            'fechaCreacion': data.get('created_at'),
            'estado': data.get('estado'),
            'estadoDisplay': data.get('estado_display'),
            'responsable': data.get('supervisor'),
            'progreso': data.get('progreso_porcentaje', 0),
        }

