from rest_framework import serializers
from .models import Empleado


class EmpleadoSerializer(serializers.ModelSerializer):
    """
    Serializer para empleados con información completa
    """
    nombre_completo = serializers.CharField(read_only=True)
    # Propiedades de compatibilidad (read-only)
    codigo = serializers.CharField(source='codigo_empleado', required=False)
    cedula = serializers.CharField(source='dpi', required=False, allow_null=True)
    cargo = serializers.CharField(source='puesto', required=False)
    salario = serializers.DecimalField(source='salario_base_q', max_digits=12, decimal_places=2, required=False)
    fecha_ingreso = serializers.DateField(source='fecha_contratacion', required=False)

    class Meta:
        model = Empleado
        fields = (
            'id', 'codigo_empleado', 'codigo', 'nombres', 'apellidos', 'nombre_completo',
            'dpi', 'cedula', 'nit', 'telefono', 'email', 
            'puesto', 'cargo', 'area_trabajo', 'turno', 'tipo_contrato',
            'salario_base_q', 'salario', 'fecha_contratacion', 'fecha_ingreso',
            'fecha_baja', 'usuario_id', 'activo',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'codigo', 'cedula', 'cargo', 'salario', 'fecha_ingreso')

    def to_internal_value(self, data):
        """
        Convierte los nombres de compatibilidad a los nombres reales de los campos
        """
        # Mapear nombres de compatibilidad a nombres reales
        if 'codigo' in data and 'codigo_empleado' not in data:
            data['codigo_empleado'] = data.pop('codigo')
        if 'cedula' in data and 'dpi' not in data:
            data['dpi'] = data.pop('cedula')
        if 'cargo' in data and 'puesto' not in data:
            data['puesto'] = data.pop('cargo')
        if 'salario' in data and 'salario_base_q' not in data:
            data['salario_base_q'] = data.pop('salario')
        if 'fecha_ingreso' in data and 'fecha_contratacion' not in data:
            data['fecha_contratacion'] = data.pop('fecha_ingreso')
        
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """
        Personalizar la representación para que coincida con el formato esperado por el frontend
        """
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo_empleado', data.get('codigo', '')),
            'nombres': data.get('nombres', ''),
            'apellidos': data.get('apellidos', ''),
            'nombreCompleto': data.get('nombre_completo', ''),
            'cedula': data.get('dpi', data.get('cedula', '')),
            'telefono': data.get('telefono', ''),
            'email': data.get('email', ''),
            'cargo': data.get('puesto', data.get('cargo', '')),
            'salario': float(data.get('salario_base_q', data.get('salario', 0))),
            'fechaIngreso': data.get('fecha_contratacion', data.get('fecha_ingreso', '')),
            'activo': data.get('activo', True),
            'created_at': data.get('created_at', ''),
            'updated_at': data.get('updated_at', ''),
            # Campos adicionales
            'nit': data.get('nit', ''),
            'areaTrabajo': data.get('area_trabajo', ''),
            'turno': data.get('turno', ''),
            'tipoContrato': data.get('tipo_contrato', ''),
            # Campos en snake_case para compatibilidad
            'fecha_ingreso': data.get('fecha_contratacion', data.get('fecha_ingreso', '')),
        }


class EmpleadoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar empleados
    """
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Empleado
        fields = (
            'id', 'codigo', 'nombres', 'apellidos', 'nombre_completo',
            'cedula', 'cargo', 'salario', 'fecha_ingreso', 'activo'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombres': data.get('nombres', ''),
            'apellidos': data.get('apellidos', ''),
            'nombreCompleto': data.get('nombre_completo', ''),
            'cedula': data.get('cedula', ''),
            'cargo': data.get('cargo', ''),
            'salario': float(data.get('salario', 0)),
            'fechaIngreso': data.get('fecha_ingreso', ''),
            'activo': data.get('activo', True),
        }


class EmpleadosStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de empleados
    """
    total_empleados = serializers.IntegerField()
    empleados_activos = serializers.IntegerField()
    empleados_inactivos = serializers.IntegerField()

