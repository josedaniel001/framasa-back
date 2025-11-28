# Serializers del módulo Taller

from rest_framework import serializers
from .models import Maquinaria, TipoMaquinaria


class MaquinariaSerializer(serializers.ModelSerializer):
    """
    Serializer para maquinaria con información completa
    """
    empresa_display = serializers.CharField(source='get_empresa_display', read_only=True)
    tipo_maquinaria_display = serializers.CharField(source='get_tipo_maquinaria_display', read_only=True)
    
    class Meta:
        model = Maquinaria
        fields = (
            'id', 'codigo', 'nombre', 'empresa', 'empresa_display',
            'tipo_maquinaria', 'tipo_maquinaria_display',
            'marca', 'modelo', 'numero_serie', 'año_fabricacion',
            'estado_actual', 'fecha_ultimo_mantenimiento', 'fecha_proximo_mantenimiento',
            'horas_operacion', 'kilometraje',
            'seguro_vigente', 'documentacion_vigente',
            'ubicacion_actual', 'observaciones', 'activo',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'empresa_display', 'tipo_maquinaria_display')

    def to_representation(self, instance):
        """
        Personalizar la representación para que coincida con el formato esperado por el frontend
        """
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'empresa': data.get('empresa', ''),
            'empresaDisplay': data.get('empresa_display', ''),
            'tipoMaquinaria': data.get('tipo_maquinaria', ''),
            'tipoMaquinariaDisplay': data.get('tipo_maquinaria_display', ''),
            'marca': data.get('marca', ''),
            'modelo': data.get('modelo', ''),
            'numeroSerie': data.get('numero_serie', ''),
            'añoFabricacion': data.get('año_fabricacion'),
            'estadoActual': data.get('estado_actual', ''),
            'fechaUltimoMantenimiento': data.get('fecha_ultimo_mantenimiento', ''),
            'fechaProximoMantenimiento': data.get('fecha_proximo_mantenimiento', ''),
            'horasOperacion': data.get('horas_operacion', 0),
            'kilometraje': data.get('kilometraje', 0),
            'seguroVigente': data.get('seguro_vigente', True),
            'documentacionVigente': data.get('documentacion_vigente', True),
            'ubicacionActual': data.get('ubicacion_actual', ''),
            'observaciones': data.get('observaciones', ''),
            'activo': data.get('activo', True),
            'createdAt': data.get('created_at', ''),
            'updatedAt': data.get('updated_at', ''),
            # Campos en snake_case para compatibilidad
            'empresa_display': data.get('empresa_display', ''),
            'tipo_maquinaria': data.get('tipo_maquinaria', ''),
            'tipo_maquinaria_display': data.get('tipo_maquinaria_display', ''),
            'estado_actual': data.get('estado_actual', ''),
            'fecha_ultimo_mantenimiento': data.get('fecha_ultimo_mantenimiento', ''),
            'fecha_proximo_mantenimiento': data.get('fecha_proximo_mantenimiento', ''),
            'horas_operacion': data.get('horas_operacion', 0),
            'seguro_vigente': data.get('seguro_vigente', True),
            'documentacion_vigente': data.get('documentacion_vigente', True),
            'ubicacion_actual': data.get('ubicacion_actual', ''),
            'created_at': data.get('created_at', ''),
            'updated_at': data.get('updated_at', ''),
        }


class MaquinariaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar maquinaria
    """
    empresa_display = serializers.CharField(source='get_empresa_display', read_only=True)
    tipo_maquinaria_display = serializers.CharField(source='get_tipo_maquinaria_display', read_only=True)
    
    class Meta:
        model = Maquinaria
        fields = (
            'id', 'codigo', 'nombre', 'empresa', 'empresa_display',
            'tipo_maquinaria', 'tipo_maquinaria_display',
            'marca', 'modelo', 'estado_actual',
            'fecha_proximo_mantenimiento',
            'seguro_vigente', 'documentacion_vigente',
            'activo'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'empresa': data.get('empresa', ''),
            'empresaDisplay': data.get('empresa_display', ''),
            'tipoMaquinaria': data.get('tipo_maquinaria', ''),
            'tipoMaquinariaDisplay': data.get('tipo_maquinaria_display', ''),
            'marca': data.get('marca', ''),
            'modelo': data.get('modelo', ''),
            'estado': data.get('estado_actual', ''),
            'proximoMantenimiento': data.get('fecha_proximo_mantenimiento', ''),
            'seguroVigente': data.get('seguro_vigente', True),
            'documentacionVigente': data.get('documentacion_vigente', True),
            'activo': data.get('activo', True),
        }
