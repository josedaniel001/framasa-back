from rest_framework import serializers
from .models import Producto, CategoriaProducto, UnidadMedida, Cliente


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

    # Campos calculados
    tiene_stock_bajo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Producto
        fields = (
            'id', 'codigo', 'nombre', 'descripcion',
            'categoria', 'categoria_id', 'categoria_nombre',
            'unidad_medida', 'unidad_medida_id', 'unidad_medida_nombre', 'unidad_medida_abreviatura',
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

    class Meta:
        model = Producto
        fields = (
            'id', 'codigo', 'nombre', 'categoria',
            'precio_venta', 'stock_actual', 'activo'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'categoria': data.get('categoria', ''),
            'precioVenta': float(data.get('precio_venta', 0)),
            'stockActual': data.get('stock_actual', 0),
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


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para clientes
    """
    fecha_registro = serializers.DateTimeField(read_only=True)
    fechaRegistro = serializers.DateTimeField(read_only=True, source='fecha_registro')

    class Meta:
        model = Cliente
        fields = (
            'id', 'nombre', 'nit', 'direccion', 'telefono', 'email',
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
            'activo': data.get('activo', True),
            'fecha_registro': data.get('fecha_registro'),
            'fechaRegistro': data.get('fechaRegistro') or data.get('fecha_registro'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at'),
        }

