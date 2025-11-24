from rest_framework import serializers
from .models import Producto, CategoriaProducto, UnidadMedida, Cliente, Proveedor, MovimientoInventario, TipoMovimiento


class CategoriaProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para categorías de productos
    """
    class Meta:
        model = CategoriaProducto
        fields = ('id', 'nombre', 'descripcion', 'activo')


class UnidadMedidaSerializer(serializers.ModelSerializer):
    """
    Serializer para unidades de medida
    """
    class Meta:
        model = UnidadMedida
        fields = ('id', 'nombre', 'abreviatura', 'activo')


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para productos con información relacionada
    """
    categoria = serializers.StringRelatedField(read_only=True)
    categoria_id = serializers.IntegerField(write_only=True, required=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    unidad_medida = serializers.StringRelatedField(read_only=True)
    unidad_medida_id = serializers.IntegerField(write_only=True, required=True)
    unidad_medida_nombre = serializers.CharField(source='unidad_medida.nombre', read_only=True)
    unidad_medida_abreviatura = serializers.CharField(source='unidad_medida.abreviatura', read_only=True)
    
    proveedor = serializers.StringRelatedField(read_only=True)
    proveedor_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)

    # Campos calculados
    tiene_stock_bajo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Producto
        fields = (
            'id', 'codigo', 'nombre', 'descripcion',
            'categoria', 'categoria_id', 'categoria_nombre',
            'unidad_medida', 'unidad_medida_id', 'unidad_medida_nombre', 'unidad_medida_abreviatura',
            'proveedor', 'proveedor_id', 'proveedor_nombre',
            'precio_venta', 'costo_unitario',
            'stock_actual', 'stock_minimo',
            'activo', 'tiene_stock_bajo',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        """
        Personalizar la representación para que coincida con el formato esperado por el frontend
        Incluye tanto los campos en camelCase para visualización como los IDs en snake_case para edición
        """
        data = super().to_representation(instance)
        # Formatear para que coincida con ProductoFerreteria del frontend
        # Incluir ambos formatos: camelCase para visualización y snake_case con IDs para edición
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'descripcion': data.get('descripcion', ''),
            # Campos en snake_case con IDs (necesarios para edición)
            'categoria_id': instance.categoria_id if hasattr(instance, 'categoria_id') else None,
            'unidad_medida_id': instance.unidad_medida_id if hasattr(instance, 'unidad_medida_id') else None,
            'proveedor_id': instance.proveedor_id if hasattr(instance, 'proveedor_id') and instance.proveedor_id else None,
            'precio_venta': float(data.get('precio_venta', 0)),
            'costo_unitario': float(data.get('costo_unitario', 0)),
            'stock_actual': data.get('stock_actual', 0),
            'stock_minimo': data.get('stock_minimo', 0),
            'activo': data.get('activo', False),
            # Campos en camelCase (para visualización)
            'categoria': data.get('categoria_nombre', ''),
            'precioVenta': float(data.get('precio_venta', 0)),
            'costoUnitario': float(data.get('costo_unitario', 0)),
            'unidadMedida': data.get('unidad_medida_nombre', ''),
            'proveedor': data.get('proveedor_nombre', '') if data.get('proveedor_nombre') else None,
            'stockActual': data.get('stock_actual', 0),
            'stockMinimo': data.get('stock_minimo', 0),
            'fechaCreacion': data.get('created_at', ''),
            'ultimaActualizacion': data.get('updated_at', ''),
        }


class ProductoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar productos
    """
    categoria = serializers.CharField(source='categoria.nombre', read_only=True)
    proveedor = serializers.CharField(source='proveedor.nombre', read_only=True, allow_null=True)

    class Meta:
        model = Producto
        fields = (
            'id', 'codigo', 'nombre', 'categoria', 'proveedor',
            'precio_venta', 'stock_actual', 'stock_minimo', 'activo'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'categoria': data.get('categoria', ''),
            'proveedor': data.get('proveedor') if data.get('proveedor') else None,
            'precioVenta': float(data.get('precio_venta', 0)),
            'precio_venta': float(data.get('precio_venta', 0)),
            'stockActual': data.get('stock_actual', 0),
            'stock_actual': data.get('stock_actual', 0),
            'stockMinimo': data.get('stock_minimo', 0),
            'stock_minimo': data.get('stock_minimo', 0),
            'activo': data.get('activo', False),
        }


class ProductosStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de productos
    """
    total_productos = serializers.IntegerField()
    productos_activos = serializers.IntegerField()
    productos_inactivos = serializers.IntegerField()
    productos_stock_bajo = serializers.IntegerField()


class ProveedorSerializer(serializers.ModelSerializer):
    """
    Serializer para proveedores
    """
    fecha_registro = serializers.DateTimeField(read_only=True)
    fechaRegistro = serializers.DateTimeField(read_only=True, source='fecha_registro')

    class Meta:
        model = Proveedor
        fields = (
            'id', 'nombre', 'nit', 'direccion', 'telefono', 'email', 'contacto',
            'activo', 'fecha_registro', 'fechaRegistro',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'fecha_registro', 'created_at', 'updated_at')

    def to_representation(self, instance):
        """
        Personalizar la representación para que coincida con el formato esperado por el frontend
        """
        data = super().to_representation(instance)
        return {
            'id': data.get('id'),
            'nombre': data.get('nombre', ''),
            'nit': data.get('nit'),
            'direccion': data.get('direccion'),
            'telefono': data.get('telefono'),
            'email': data.get('email'),
            'contacto': data.get('contacto'),
            'activo': data.get('activo', True),
            'fecha_registro': data.get('fecha_registro'),
            'fechaRegistro': data.get('fechaRegistro') or data.get('fecha_registro'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at'),
        }


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para clientes
    """
    fecha_registro = serializers.DateTimeField(read_only=True)
    fechaRegistro = serializers.DateTimeField(read_only=True, source='fecha_registro')

    # Campos calculados de fiado
    credito_disponible = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    puede_comprar_fiado = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cliente
        fields = (
            'id', 'nombre', 'nit', 'direccion', 'telefono', 'email',
            'activo', 'permite_fiado', 'limite_credito', 'saldo_actual',
            'credito_disponible', 'puede_comprar_fiado',
            'fecha_registro', 'fechaRegistro',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'fecha_registro', 'created_at', 'updated_at', 'credito_disponible', 'puede_comprar_fiado')

    def to_representation(self, instance):
        """
        Personalizar la representación para que coincida con el formato esperado por el frontend
        """
        data = super().to_representation(instance)
        return {
            'id': data.get('id'),
            'nombre': data.get('nombre', ''),
            'nit': data.get('nit'),
            'direccion': data.get('direccion'),
            'telefono': data.get('telefono'),
            'email': data.get('email'),
            'activo': data.get('activo', True),
            'permite_fiado': data.get('permite_fiado', False),
            'permiteFiado': data.get('permite_fiado', False),
            'limite_credito': float(data.get('limite_credito', 0)),
            'limiteCredito': float(data.get('limite_credito', 0)),
            'saldo_actual': float(data.get('saldo_actual', 0)),
            'saldoActual': float(data.get('saldo_actual', 0)),
            'credito_disponible': float(data.get('credito_disponible', 0)),
            'creditoDisponible': float(data.get('credito_disponible', 0)),
            'puede_comprar_fiado': data.get('puede_comprar_fiado', False),
            'puedeComprarFiado': data.get('puede_comprar_fiado', False),
            'fecha_registro': data.get('fecha_registro'),
            'fechaRegistro': data.get('fechaRegistro') or data.get('fecha_registro'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at'),
        }


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    """
    Serializer para movimientos de inventario
    """
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = MovimientoInventario
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
        if tipo in [TipoMovimiento.ENTRADA, TipoMovimiento.SALIDA,
                    TipoMovimiento.DEVOLUCION, TipoMovimiento.TRANSFERENCIA]:
            if cantidad <= 0:
                raise serializers.ValidationError({
                    'cantidad': 'La cantidad debe ser mayor a 0 para este tipo de movimiento'
                })

        # Para SALIDA y TRANSFERENCIA: verificar que haya stock suficiente
        if tipo in [TipoMovimiento.SALIDA, TipoMovimiento.TRANSFERENCIA]:
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
