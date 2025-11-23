from rest_framework import serializers
from .models import AgregadoPiedrinera, Camion


class AgregadoPiedrineraSerializer(serializers.ModelSerializer):
    """
    Serializer para agregados de piedrinera con información completa
    """
    # Campos calculados
    tiene_stock_bajo = serializers.BooleanField(read_only=True)

    class Meta:
        model = AgregadoPiedrinera
        fields = (
            'id', 'codigo', 'nombre', 'descripcion',
            'tipo', 'granulometria',
            'precio_venta_m3', 'costo_produccion_m3',
            'stock_actual_m3', 'stock_minimo_m3',
            'ubicacion', 'humedad_porcentaje', 'calidad',
            'proveedor', 'fecha_ultima_entrada',
            'activo', 'tiene_stock_bajo',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        """
        Personalizar la representación para que coincida con el formato esperado por el frontend
        """
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'descripcion': data.get('descripcion', ''),
            'tipo': data.get('tipo', ''),
            'granulometria': data.get('granulometria', ''),
            # Campos en snake_case (para compatibilidad)
            'precio_venta_m3': float(data.get('precio_venta_m3', 0)),
            'costo_produccion_m3': float(data.get('costo_produccion_m3', 0)),
            'stock_actual_m3': float(data.get('stock_actual_m3', 0)),
            'stock_minimo_m3': float(data.get('stock_minimo_m3', 0)),
            'ubicacion': data.get('ubicacion', ''),
            'humedad_porcentaje': float(data.get('humedad_porcentaje', 0)) if data.get('humedad_porcentaje') else None,
            'calidad': data.get('calidad', ''),
            'proveedor': data.get('proveedor', ''),
            'fecha_ultima_entrada': data.get('fecha_ultima_entrada', ''),
            'activo': data.get('activo', False),
            'tiene_stock_bajo': data.get('tiene_stock_bajo', False),
            # Campos en camelCase (para visualización en frontend)
            'precioVentaPorMetroCubico': float(data.get('precio_venta_m3', 0)),
            'costoProduccionPorMetroCubico': float(data.get('costo_produccion_m3', 0)),
            'stockActualMetrosCubicos': float(data.get('stock_actual_m3', 0)),
            'stockMinimoMetrosCubicos': float(data.get('stock_minimo_m3', 0)),
            'humedadPorcentaje': float(data.get('humedad_porcentaje', 0)) if data.get('humedad_porcentaje') else None,
            'fechaUltimaEntrada': data.get('fecha_ultima_entrada', ''),
            'fechaCreacion': data.get('created_at', ''),
            'ultimaActualizacion': data.get('updated_at', ''),
        }


class AgregadoPiedrineraListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar agregados
    """
    class Meta:
        model = AgregadoPiedrinera
        fields = (
            'id', 'codigo', 'nombre', 'tipo', 'granulometria',
            'precio_venta_m3', 'stock_actual_m3', 'stock_minimo_m3',
            'activo', 'ubicacion', 'calidad', 'proveedor'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'tipo': data.get('tipo', ''),
            'granulometria': data.get('granulometria', ''),
            'precioVenta': float(data.get('precio_venta_m3', 0)),
            'stock': float(data.get('stock_actual_m3', 0)),
            'stockMinimo': float(data.get('stock_minimo_m3', 0)),
            'activo': data.get('activo', False),
            'ubicacion': data.get('ubicacion', ''),
            'calidad': data.get('calidad', ''),
            'proveedor': data.get('proveedor', ''),
        }


class AgregadosStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de agregados
    """
    total_agregados = serializers.IntegerField()
    agregados_activos = serializers.IntegerField()
    agregados_inactivos = serializers.IntegerField()
    agregados_stock_bajo = serializers.IntegerField()


class CamionSerializer(serializers.ModelSerializer):
    """
    Serializer para camiones con información completa
    """
    class Meta:
        model = Camion
        fields = (
            'id', 'placa', 'marca', 'modelo',
            'capacidad_m3', 'estado_actual',
            'fecha_ultimo_mantenimiento', 'fecha_proximo_mantenimiento',
            'kilometraje', 'horas_operacion', 'consumo_l_100km',
            'seguro_vigente', 'revision_tecnica_vigente', 'documentacion_vigente',
            'observaciones', 'activo',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        """
        Personalizar la representación para que coincida con el formato esperado por el frontend
        """
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'placa': data.get('placa', ''),
            'marca': data.get('marca', ''),
            'modelo': data.get('modelo', ''),
            'capacidad_m3': float(data.get('capacidad_m3', 0)),
            'estado_actual': data.get('estado_actual', ''),
            'fecha_ultimo_mantenimiento': data.get('fecha_ultimo_mantenimiento', ''),
            'fecha_proximo_mantenimiento': data.get('fecha_proximo_mantenimiento', ''),
            'kilometraje': data.get('kilometraje', 0),
            'horas_operacion': data.get('horas_operacion', 0),
            'consumo_l_100km': float(data.get('consumo_l_100km', 0)),
            'seguro_vigente': data.get('seguro_vigente', True),
            'revision_tecnica_vigente': data.get('revision_tecnica_vigente', True),
            'documentacion_vigente': data.get('documentacion_vigente', True),
            'observaciones': data.get('observaciones', ''),
            'activo': data.get('activo', True),
            'created_at': data.get('created_at', ''),
            'updated_at': data.get('updated_at', ''),
            # Campos en camelCase para compatibilidad con frontend
            'capacidadMetrosCubicos': float(data.get('capacidad_m3', 0)),
            'estado': data.get('estado_actual', ''),
            'ultimoMantenimiento': data.get('fecha_ultimo_mantenimiento', ''),
            'proximoMantenimiento': data.get('fecha_proximo_mantenimiento', ''),
            'horasOperacion': data.get('horas_operacion', 0),
            'consumoCombustible': float(data.get('consumo_l_100km', 0)),
            'seguroVigente': data.get('seguro_vigente', True),
            'revisionTecnicaVigente': data.get('revision_tecnica_vigente', True),
            'documentacionVigente': data.get('documentacion_vigente', True),
        }


class CamionListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar camiones
    """
    class Meta:
        model = Camion
        fields = (
            'id', 'placa', 'marca', 'modelo',
            'capacidad_m3', 'estado_actual',
            'fecha_proximo_mantenimiento',
            'seguro_vigente', 'revision_tecnica_vigente', 'documentacion_vigente',
            'activo'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'placa': data.get('placa', ''),
            'marca': data.get('marca', ''),
            'modelo': data.get('modelo', ''),
            'capacidadMetrosCubicos': float(data.get('capacidad_m3', 0)),
            'estado': data.get('estado_actual', ''),
            'proximoMantenimiento': data.get('fecha_proximo_mantenimiento', ''),
            'seguroVigente': data.get('seguro_vigente', True),
            'revisionTecnicaVigente': data.get('revision_tecnica_vigente', True),
            'documentacionVigente': data.get('documentacion_vigente', True),
            'activo': data.get('activo', True),
        }

