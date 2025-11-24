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
    stock_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock_minimo_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    productos_stock_bajo = serializers.IntegerField()
    valor_inventario_estimado = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    unidades = serializers.CharField()


class EstadisticaPredictivaSerializer(serializers.Serializer):
    """Serializer para estadísticas predictivas"""
    empresa = serializers.CharField()
    producto_id = serializers.IntegerField()
    producto_codigo = serializers.CharField()
    producto_nombre = serializers.CharField()
    stock_actual = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock_minimo = serializers.DecimalField(max_digits=12, decimal_places=2)
    promedio_ventas_diarias = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    promedio_ventas_semanales = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    promedio_ventas_mensuales = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    dias_restantes_estimados = serializers.IntegerField(required=False, allow_null=True)
    necesita_reposicion = serializers.BooleanField()
    tendencia = serializers.CharField(required=False, allow_null=True)  # 'creciente', 'decreciente', 'estable'
    unidades = serializers.CharField()


class ReporteInventarioUnificadoSerializer(serializers.Serializer):
    """Serializer para el reporte completo de inventario unificado"""
    resumen_general = serializers.DictField()
    por_empresa = InventarioUnificadoSerializer(many=True)
    total_general = serializers.DictField()

