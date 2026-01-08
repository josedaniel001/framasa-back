from rest_framework import serializers
from decimal import Decimal


class ProductoVendidoSerializer(serializers.Serializer):
    """Serializer para productos más vendidos"""
    producto_id = serializers.IntegerField()
    producto_codigo = serializers.CharField()
    producto_nombre = serializers.CharField()
    empresa = serializers.CharField()  # 'ferreteria', 'bloquera', 'piedrinera'
    cantidad_vendida = serializers.DecimalField(max_digits=12, decimal_places=2)
    unidades = serializers.CharField()  # 'unidades' o 'm³'
    valor_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)


class InventarioUnificadoSerializer(serializers.Serializer):
    """Serializer para inventario unificado"""
    empresa = serializers.CharField()
    total_productos = serializers.IntegerField()
    productos_activos = serializers.IntegerField()
    productos_inactivos = serializers.IntegerField()
    productos_stock_bajo = serializers.IntegerField()
    valor_inventario_estimado = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    unidades = serializers.CharField()


class EstadisticaPredictivaSerializer(serializers.Serializer):
    """Serializer para estadísticas predictivas por producto"""
    producto_id = serializers.IntegerField()
    producto_codigo = serializers.CharField()
    producto_nombre = serializers.CharField()
    empresa = serializers.CharField()
    periodo = serializers.IntegerField()
    ventas_q = serializers.DecimalField(max_digits=12, decimal_places=2)
    prom_diario_q = serializers.DecimalField(max_digits=12, decimal_places=2)
    tendencia_porcentaje = serializers.DecimalField(max_digits=6, decimal_places=1)
    proyeccion_30d_q = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock_actual = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    dias_stock = serializers.IntegerField(required=False, allow_null=True)
    riesgo_stock = serializers.CharField(required=False, allow_null=True)  # 'Alto', 'Medio', 'Bajo', 'Sin datos'
    recomendacion = serializers.CharField()


class ReporteInventarioUnificadoSerializer(serializers.Serializer):
    """Serializer para el reporte completo de inventario unificado"""
    resumen_general = serializers.DictField()
    por_empresa = InventarioUnificadoSerializer(many=True)
    total_general = serializers.DictField()

