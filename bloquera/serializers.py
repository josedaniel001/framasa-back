from rest_framework import serializers
from .models import ProductoBloquera, MovimientoInventarioBloquera, TipoMovimientoBloquera


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
            'precio_unitario', 'costo_produccion',
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
            'precio_unitario', 'stock_actual', 'activo'
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
            'stockActual': data.get('stock_actual', 0),
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
            'usuario_nombre', 'tipo_display'
        )

    def validate(self, data):
        """
        Validación personalizada
        """
        tipo = data.get('tipo')
        cantidad = data.get('cantidad')
        producto = data.get('producto')

        # Para ENTRADA, SALIDA, DEVOLUCION, TRANSFERENCIA: cantidad debe ser positiva
        if tipo in [TipoMovimientoBloquera.ENTRADA, TipoMovimientoBloquera.SALIDA,
                    TipoMovimientoBloquera.DEVOLUCION, TipoMovimientoBloquera.TRANSFERENCIA]:
            if cantidad <= 0:
                raise serializers.ValidationError({
                    'cantidad': 'La cantidad debe ser mayor a 0 para este tipo de movimiento'
                })

        # Para SALIDA y TRANSFERENCIA: verificar que haya stock suficiente
        if tipo in [TipoMovimientoBloquera.SALIDA, TipoMovimientoBloquera.TRANSFERENCIA]:
            if producto and producto.stock_actual < cantidad:
                raise serializers.ValidationError({
                    'cantidad': f'Stock insuficiente. Stock actual: {producto.stock_actual}'
                })

        return data

    def create(self, validated_data):
        """
        Crear movimiento y asignar usuario automáticamente
        """
        # Obtener el usuario del request
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        
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

