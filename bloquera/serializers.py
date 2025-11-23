from rest_framework import serializers
from .models import ProductoBloquera


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

