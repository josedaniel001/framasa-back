from rest_framework import serializers
from .models import Empleado, Asistencia, Nomina, NominaDetalle, PagoNomina, Cargo


class EmpleadoSerializer(serializers.ModelSerializer):
    """
    Serializer para empleados con información completa
    """
    nombre_completo = serializers.CharField(read_only=True)
    # Propiedades de compatibilidad (read-only)
    codigo = serializers.CharField(source='codigo_empleado', required=False)
    cedula = serializers.CharField(source='dpi', required=False, allow_null=True)
    # Campo para manejar los cargos (ManyToMany)
    cargos = serializers.PrimaryKeyRelatedField(
        queryset=Cargo.objects.all(),
        many=True,
        required=False,
        allow_empty=True
    )
    cargo = serializers.CharField(read_only=True)  # Propiedad computada
    salario = serializers.DecimalField(source='salario_base_q', max_digits=12, decimal_places=2, required=False)
    fecha_ingreso = serializers.DateField(source='fecha_contratacion', required=False)

    class Meta:
        model = Empleado
        fields = (
            'id', 'codigo_empleado', 'codigo', 'nombres', 'apellidos', 'nombre_completo',
            'dpi', 'cedula', 'nit', 'telefono', 'email',
            'cargos', 'cargo', 'area_trabajo', 'turno', 'tipo_contrato',
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
        # Nota: 'cargo' ahora se maneja como ManyToMany 'cargos', no como campo único 'puesto'
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


# Mapeo de estados frontend <-> backend
ESTADO_FRONTEND_TO_BACKEND = {
    'presente': 'Presente',
    'descanso': 'Descanso',
    'vacaciones': 'Vacaciones',
    'permiso_con_goce': 'Permiso con goce',
    'permiso_sin_goce': 'Permiso sin goce',
    'licencia_medica': 'Licencia Medica',
    'ausente': 'Ausente',
}

ESTADO_BACKEND_TO_FRONTEND = {v: k for k, v in ESTADO_FRONTEND_TO_BACKEND.items()}


class AsistenciaSerializer(serializers.ModelSerializer):
    """
    Serializer completo para asistencias
    """
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empleado_codigo = serializers.CharField(source='empleado.codigo_empleado', read_only=True)
    horas_trabajadas = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Asistencia
        fields = (
            'id', 'empleado', 'empleado_nombre', 'empleado_codigo',
            'usuario', 'fecha', 'hora_entrada', 'hora_salida',
            'estado', 'fecha_retorno', 'observaciones', 'activo',
            'horas_trabajadas', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'empleado_nombre', 'empleado_codigo', 'horas_trabajadas')

    def to_internal_value(self, data):
        """
        Convierte los valores del frontend al formato de la base de datos
        """
        # Mapear estado de frontend a backend
        if 'estado' in data:
            estado_frontend = data.get('estado', '').lower().replace(' ', '_')
            data['estado'] = ESTADO_FRONTEND_TO_BACKEND.get(estado_frontend, data['estado'])
        
        # Convertir empleadoId a empleado
        if 'empleadoId' in data and 'empleado' not in data:
            data['empleado'] = data.pop('empleadoId')
        
        # Convertir horaEntrada/horaSalida a snake_case
        if 'horaEntrada' in data:
            data['hora_entrada'] = data.pop('horaEntrada') or None
        if 'horaSalida' in data:
            data['hora_salida'] = data.pop('horaSalida') or None
        if 'fechaRetorno' in data:
            data['fecha_retorno'] = data.pop('fechaRetorno') or None
        
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """
        Personaliza la representación para el frontend
        """
        data = super().to_representation(instance)
        
        # Mapear estado de backend a frontend
        estado_backend = data.get('estado', '')
        estado_frontend = ESTADO_BACKEND_TO_FRONTEND.get(estado_backend, estado_backend.lower().replace(' ', '_'))
        
        return {
            'id': str(data.get('id', '')),
            'empleadoId': str(data.get('empleado', '')),
            'empleado': data.get('empleado_nombre', ''),
            'codigo': data.get('empleado_codigo', ''),
            'fecha': data.get('fecha', ''),
            'horaEntrada': data.get('hora_entrada', '') or '-',
            'horaSalida': data.get('hora_salida', '') or '-',
            'horasTrabajadas': data.get('horas_trabajadas', 0),
            'estado': estado_frontend,
            'fechaRetorno': data.get('fecha_retorno', '') or '',
            'observaciones': data.get('observaciones', '') or '',
            'activo': data.get('activo', True),
            'created_at': data.get('created_at', ''),
            'updated_at': data.get('updated_at', ''),
        }


class AsistenciaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar asistencias
    """
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empleado_codigo = serializers.CharField(source='empleado.codigo_empleado', read_only=True)
    horas_trabajadas = serializers.FloatField(read_only=True)

    class Meta:
        model = Asistencia
        fields = (
            'id', 'empleado', 'empleado_nombre', 'empleado_codigo',
            'fecha', 'hora_entrada', 'hora_salida', 'estado',
            'fecha_retorno', 'observaciones', 'horas_trabajadas', 'activo'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Mapear estado de backend a frontend
        estado_backend = data.get('estado', '')
        estado_frontend = ESTADO_BACKEND_TO_FRONTEND.get(estado_backend, estado_backend.lower().replace(' ', '_'))
        
        return {
            'id': str(data.get('id', '')),
            'empleadoId': str(data.get('empleado', '')),
            'empleado': data.get('empleado_nombre', ''),
            'codigo': data.get('empleado_codigo', ''),
            'fecha': data.get('fecha', ''),
            'horaEntrada': data.get('hora_entrada', '') or '-',
            'horaSalida': data.get('hora_salida', '') or '-',
            'horasTrabajadas': data.get('horas_trabajadas', 0),
            'estado': estado_frontend,
            'fechaRetorno': data.get('fecha_retorno', '') or '',
            'observaciones': data.get('observaciones', '') or '',
            'activo': data.get('activo', True),
        }


class AsistenciaStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de asistencias
    """
    total_registros = serializers.IntegerField()
    presentes = serializers.IntegerField()
    ausentes = serializers.IntegerField()
    licencias = serializers.IntegerField()
    vacaciones = serializers.IntegerField()
    descansos = serializers.IntegerField()
    permisos_con_goce = serializers.IntegerField()
    permisos_sin_goce = serializers.IntegerField()
    horas_totales = serializers.FloatField()
    porcentaje_asistencia = serializers.FloatField()


# ==================== SERIALIZERS DE NÓMINAS ====================

class PagoNominaSerializer(serializers.ModelSerializer):
    """
    Serializer para pagos de nómina
    """
    empleado_nombre = serializers.CharField(source='nomina_detalle.empleado.nombre_completo', read_only=True)
    
    class Meta:
        model = PagoNomina
        fields = (
            'id', 'nomina_detalle', 'empleado_nombre', 'forma_pago', 'monto', 'moneda',
            'fecha_pago', 'usuario', 'banco', 'numero_cheque', 'cuenta_bancaria',
            'fecha_cobro', 'anulado', 'motivo_anulacion', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'empleado_nombre')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'nominaDetalleId': str(data.get('nomina_detalle', '')),
            'empleadoNombre': data.get('empleado_nombre', ''),
            'formaPago': data.get('forma_pago', ''),
            'monto': float(data.get('monto', 0)),
            'moneda': data.get('moneda', 'GTQ'),
            'fechaPago': data.get('fecha_pago', ''),
            'usuarioId': str(data.get('usuario', '')) if data.get('usuario') else None,
            'banco': data.get('banco', ''),
            'numeroCheque': data.get('numero_cheque', ''),
            'cuentaBancaria': data.get('cuenta_bancaria', ''),
            'fechaCobro': data.get('fecha_cobro', ''),
            'anulado': data.get('anulado', False),
            'motivoAnulacion': data.get('motivo_anulacion', ''),
            'createdAt': data.get('created_at', ''),
            'updatedAt': data.get('updated_at', ''),
        }


class NominaDetalleSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalle de nómina
    """
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empleado_codigo = serializers.CharField(source='empleado.codigo_empleado', read_only=True)
    pagos = PagoNominaSerializer(many=True, read_only=True)
    
    class Meta:
        model = NominaDetalle
        fields = (
            'id', 'nomina', 'empleado', 'empleado_nombre', 'empleado_codigo',
            'dias_trabajados', 'dias_descanso', 'dias_vacaciones', 'dias_permiso_con_goce',
            'dias_permiso_sin_goce', 'dias_licencia_medica', 'dias_ausente',
            'salario_base_mensual', 'salario_base_periodo', 'salario_base_devengado',
            'horas_extra', 'monto_horas_extra', 'bonificaciones',
            'igss', 'isr', 'otros_descuentos',
            'total_devengado', 'total_descuentos', 'salario_neto',
            'estado', 'pagado', 'metodo_pago', 'fecha_pagado',
            'observaciones', 'activo', 'pagos', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'empleado_nombre', 'empleado_codigo', 'pagos')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'nominaId': str(data.get('nomina', '')),
            'empleadoId': str(data.get('empleado', '')),
            'empleadoNombre': data.get('empleado_nombre', ''),
            'empleadoCodigo': data.get('empleado_codigo', ''),
            # Días
            'diasTrabajados': data.get('dias_trabajados', 0),
            'diasDescanso': data.get('dias_descanso', 0),
            'diasVacaciones': data.get('dias_vacaciones', 0),
            'diasPermisoConGoce': data.get('dias_permiso_con_goce', 0),
            'diasPermisoSinGoce': data.get('dias_permiso_sin_goce', 0),
            'diasLicenciaMedica': data.get('dias_licencia_medica', 0),
            'diasAusente': data.get('dias_ausente', 0),
            # Salarios
            'salarioBaseMensual': float(data.get('salario_base_mensual', 0)),
            'salarioBasePeriodo': float(data.get('salario_base_periodo', 0)),
            'salarioBaseDevengado': float(data.get('salario_base_devengado', 0)),
            # Devengado
            'horasExtra': float(data.get('horas_extra', 0)),
            'montoHorasExtra': float(data.get('monto_horas_extra', 0)),
            'bonificaciones': float(data.get('bonificaciones', 0)),
            # Deducciones
            'igss': float(data.get('igss', 0)),
            'isr': float(data.get('isr', 0)),
            'otrosDescuentos': float(data.get('otros_descuentos', 0)),
            # Totales
            'totalDevengado': float(data.get('total_devengado', 0)),
            'totalDescuentos': float(data.get('total_descuentos', 0)),
            'salarioNeto': float(data.get('salario_neto', 0)),
            # Estado
            'estado': data.get('estado', ''),
            'pagado': data.get('pagado', False),
            'metodoPago': data.get('metodo_pago', ''),
            'fechaPagado': data.get('fecha_pagado', ''),
            'observaciones': data.get('observaciones', ''),
            'activo': data.get('activo', True),
            'pagos': data.get('pagos', []),
            'createdAt': data.get('created_at', ''),
            'updatedAt': data.get('updated_at', ''),
        }


class NominaDetalleListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar detalles de nómina
    """
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empleado_codigo = serializers.CharField(source='empleado.codigo_empleado', read_only=True)
    
    class Meta:
        model = NominaDetalle
        fields = (
            'id', 'nomina', 'empleado', 'empleado_nombre', 'empleado_codigo',
            'dias_trabajados', 'salario_base_periodo', 'total_devengado',
            'total_descuentos', 'salario_neto', 'estado', 'pagado', 'metodo_pago', 'activo'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'nominaId': str(data.get('nomina', '')),
            'empleadoId': str(data.get('empleado', '')),
            'empleadoNombre': data.get('empleado_nombre', ''),
            'empleadoCodigo': data.get('empleado_codigo', ''),
            'diasTrabajados': data.get('dias_trabajados', 0),
            'salarioBasePeriodo': float(data.get('salario_base_periodo', 0)),
            'totalDevengado': float(data.get('total_devengado', 0)),
            'totalDescuentos': float(data.get('total_descuentos', 0)),
            'salarioNeto': float(data.get('salario_neto', 0)),
            'estado': data.get('estado', ''),
            'pagado': data.get('pagado', False),
            'metodoPago': data.get('metodo_pago', ''),
            'activo': data.get('activo', True),
        }


class NominaSerializer(serializers.ModelSerializer):
    """
    Serializer completo para nóminas
    """
    total_empleados = serializers.IntegerField(read_only=True)
    total_devengado = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_descuentos = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_neto = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_pagado = serializers.IntegerField(read_only=True)
    total_pendientes = serializers.IntegerField(read_only=True)
    total_anulados = serializers.IntegerField(read_only=True)
    # Usar serializer completo para incluir todos los campos de detalle
    detalles = NominaDetalleSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = Nomina
        fields = (
            'id', 'tipo_periodo', 'fecha_inicio', 'fecha_fin', 'fecha_pago',
            'estado', 'usuario', 'usuario_nombre', 'observaciones', 'activo',
            'total_empleados', 'total_devengado', 'total_descuentos', 'total_neto', 'total_pagado',
            'total_pendientes', 'total_anulados', 'detalles', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'usuario_nombre', 
                           'total_empleados', 'total_devengado', 'total_descuentos', 'total_neto', 
                           'total_pagado', 'total_pendientes', 'total_anulados')

    def to_internal_value(self, data):
        """
        Convierte los valores del frontend al formato de la base de datos
        """
        # Convertir camelCase a snake_case
        if 'tipoPeriodo' in data and 'tipo_periodo' not in data:
            data['tipo_periodo'] = data.pop('tipoPeriodo')
        if 'fechaInicio' in data and 'fecha_inicio' not in data:
            data['fecha_inicio'] = data.pop('fechaInicio')
        if 'fechaFin' in data and 'fecha_fin' not in data:
            data['fecha_fin'] = data.pop('fechaFin')
        if 'fechaPago' in data and 'fecha_pago' not in data:
            data['fecha_pago'] = data.pop('fechaPago')
        if 'empleadosIncluidos' in data:
            # Este campo se usa para filtrar, no se guarda en la BD
            data.pop('empleadosIncluidos')
        
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'tipoPeriodo': data.get('tipo_periodo', ''),
            'fechaInicio': data.get('fecha_inicio', ''),
            'fechaFin': data.get('fecha_fin', ''),
            'fechaPago': data.get('fecha_pago', ''),
            'estado': data.get('estado', ''),
            'usuarioId': str(data.get('usuario', '')) if data.get('usuario') else None,
            'usuarioNombre': data.get('usuario_nombre', ''),
            'observaciones': data.get('observaciones', ''),
            'activo': data.get('activo', True),
            'totalEmpleados': data.get('total_empleados', 0),
            'totalDevengado': float(data.get('total_devengado', 0)),
            'totalDescuentos': float(data.get('total_descuentos', 0)),
            'totalNeto': float(data.get('total_neto', 0)),
            'totalPagado': data.get('total_pagado', 0),
            'totalPendientes': data.get('total_pendientes', 0),
            'totalAnulados': data.get('total_anulados', 0),
            'detalles': data.get('detalles', []),
            'createdAt': data.get('created_at', ''),
            'updatedAt': data.get('updated_at', ''),
        }


class NominaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar nóminas
    """
    total_empleados = serializers.IntegerField(read_only=True)
    total_devengado = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_descuentos = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_neto = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_pagado = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Nomina
        fields = (
            'id', 'tipo_periodo', 'fecha_inicio', 'fecha_fin', 'fecha_pago',
            'estado', 'activo', 'total_empleados', 'total_devengado', 'total_descuentos', 
            'total_neto', 'total_pagado', 'created_at'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'tipoPeriodo': data.get('tipo_periodo', ''),
            'fechaInicio': data.get('fecha_inicio', ''),
            'fechaFin': data.get('fecha_fin', ''),
            'fechaPago': data.get('fecha_pago', ''),
            'estado': data.get('estado', ''),
            'activo': data.get('activo', True),
            'totalEmpleados': data.get('total_empleados', 0),
            'totalDevengado': float(data.get('total_devengado', 0)),
            'totalDescuentos': float(data.get('total_descuentos', 0)),
            'totalNeto': float(data.get('total_neto', 0)),
            'totalPagado': data.get('total_pagado', 0),
            'createdAt': data.get('created_at', ''),
        }


class NominaStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de nóminas
    """
    total_nominas = serializers.IntegerField()
    nominas_abiertas = serializers.IntegerField()
    nominas_calculadas = serializers.IntegerField()
    nominas_cerradas = serializers.IntegerField()
    nominas_pagadas = serializers.IntegerField()
    total_empleados_nomina = serializers.IntegerField()
    total_devengado_global = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_descuentos_global = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_neto_global = serializers.DecimalField(max_digits=14, decimal_places=2)


class CargoSerializer(serializers.ModelSerializer):
    """
    Serializer para cargos/puestos
    """

    class Meta:
        model = Cargo
        fields = (
            'id', 'codigo', 'nombre', 'descripcion', 'activo',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo': data.get('codigo', ''),
            'nombre': data.get('nombre', ''),
            'descripcion': data.get('descripcion', ''),
            'activo': data.get('activo', True),
            'created_at': data.get('created_at', ''),
            'updated_at': data.get('updated_at', ''),
        }
