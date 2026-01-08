from rest_framework import serializers
from .models import AgregadoPiedrinera, Camion, MovimientoInventarioPiedrinera, TipoMovimientoPiedrinera, ProduccionPiedrinera, EstadoProduccionPiedrinera


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
            'precio_venta_m3', 'precio_descuento_m3', 'costo_produccion_m3',
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
            'precio_descuento_m3': float(data.get('precio_descuento_m3')) if data.get('precio_descuento_m3') is not None else None,
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
            'precioDescuentoPorMetroCubico': float(data.get('precio_descuento_m3')) if data.get('precio_descuento_m3') is not None else None,
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
            'precio_venta_m3', 'precio_descuento_m3', 'costo_produccion_m3',
            'stock_actual_m3', 'stock_minimo_m3',
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
            'precioDescuento': float(data.get('precio_descuento_m3')) if data.get('precio_descuento_m3') is not None else None,
            'costo_produccion_m3': float(data.get('costo_produccion_m3', 0)),
            'costoProduccionPorMetroCubico': float(data.get('costo_produccion_m3', 0)),
            'stock': float(data.get('stock_actual_m3', 0)),
            'stock_actual_m3': float(data.get('stock_actual_m3', 0)),
            'stockActualMetrosCubicos': float(data.get('stock_actual_m3', 0)),
            'stockMinimo': float(data.get('stock_minimo_m3', 0)),
            'stock_minimo_m3': float(data.get('stock_minimo_m3', 0)),
            'stockMinimoMetrosCubicos': float(data.get('stock_minimo_m3', 0)),
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


class MovimientoInventarioPiedrineraSerializer(serializers.ModelSerializer):
    """
    Serializer para movimientos de inventario de piedrinera
    Usa DecimalField para manejar cantidades en m³ con decimales
    """
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = MovimientoInventarioPiedrinera
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
        from decimal import Decimal
        tipo = data.get('tipo')
        cantidad = data.get('cantidad')
        producto = data.get('producto')

        # Para ENTRADA, SALIDA, DEVOLUCION, TRANSFERENCIA: cantidad debe ser positiva
        if tipo in [TipoMovimientoPiedrinera.ENTRADA, TipoMovimientoPiedrinera.SALIDA,
                    TipoMovimientoPiedrinera.DEVOLUCION, TipoMovimientoPiedrinera.TRANSFERENCIA]:
            if cantidad <= Decimal('0'):
                raise serializers.ValidationError({
                    'cantidad': 'La cantidad debe ser mayor a 0 para este tipo de movimiento'
                })

        # Para SALIDA y TRANSFERENCIA: verificar que haya stock suficiente
        if tipo in [TipoMovimientoPiedrinera.SALIDA, TipoMovimientoPiedrinera.TRANSFERENCIA]:
            if producto and producto.stock_actual_m3 < cantidad:
                raise serializers.ValidationError({
                    'cantidad': f'Stock insuficiente. Stock actual: {producto.stock_actual_m3} m³'
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
            'cantidad': float(data.get('cantidad', 0)),
            'stockAnterior': float(data.get('stock_anterior', 0)),
            'stockNuevo': float(data.get('stock_nuevo', 0)),
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


class ProduccionPiedrineraSerializer(serializers.ModelSerializer):
    """
    Serializer para producción de piedrinera con información completa
    """
    agregado_codigo = serializers.CharField(source='agregado.codigo', read_only=True)
    agregado_nombre = serializers.CharField(source='agregado.nombre', read_only=True)
    supervisor_nombre = serializers.SerializerMethodField()
    operador_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    eficiencia_produccion = serializers.FloatField(read_only=True)
    costo_por_m3 = serializers.FloatField(read_only=True)
    duracion_produccion = serializers.FloatField(read_only=True)

    class Meta:
        model = ProduccionPiedrinera
        fields = (
            'id', 'codigo_lote',
            'agregado', 'agregado_id', 'agregado_codigo', 'agregado_nombre',
            'fecha_produccion', 'hora_inicio_produccion', 'hora_fin_produccion',
            'supervisor', 'supervisor_id', 'supervisor_nombre',
            'operador', 'operador_id', 'operador_nombre',
            'volumen_planificado_m3', 'volumen_producido_m3',
            'costo_total_q', 'estado', 'estado_display',
            'calidad', 'observaciones', 'equipos_usados',
            'eficiencia_produccion', 'costo_por_m3', 'duracion_produccion',
            'activo', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'eficiencia_produccion', 'costo_por_m3', 'duracion_produccion',
            'estado_display', 'created_at', 'updated_at'
        )

    def get_supervisor_nombre(self, obj):
        if obj.supervisor:
            return f"{obj.supervisor.nombres} {obj.supervisor.apellidos}"
        return None

    def get_operador_nombre(self, obj):
        if obj.operador:
            return f"{obj.operador.nombres} {obj.operador.apellidos}"
        return None

    def to_representation(self, instance):
        """
        Personalizar la representación para el frontend
        """
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo_lote': data.get('codigo_lote', ''),
            'agregado': {
                'id': instance.agregado_id,
                'codigo': data.get('agregado_codigo'),
                'nombre': data.get('agregado_nombre'),
            },
            'agregado_id': instance.agregado_id,
            'agregado_codigo': data.get('agregado_codigo'),
            'agregado_nombre': data.get('agregado_nombre'),
            'fecha_produccion': data.get('fecha_produccion', ''),
            'hora_inicio_produccion': data.get('hora_inicio_produccion', ''),
            'hora_fin_produccion': data.get('hora_fin_produccion'),
            'supervisor': {
                'id': instance.supervisor_id,
                'nombre': data.get('supervisor_nombre'),
            } if instance.supervisor_id else None,
            'supervisor_id': instance.supervisor_id,
            'supervisor_nombre': data.get('supervisor_nombre'),
            'operador': {
                'id': instance.operador_id,
                'nombre': data.get('operador_nombre'),
            } if instance.operador_id else None,
            'operador_id': instance.operador_id,
            'operador_nombre': data.get('operador_nombre'),
            'volumen_planificado_m3': float(data.get('volumen_planificado_m3', 0)),
            'volumen_producido_m3': float(data.get('volumen_producido_m3', 0)),
            'costo_total_q': float(data.get('costo_total_q', 0)),
            'estado': data.get('estado', ''),
            'estado_display': data.get('estado_display', ''),
            'calidad': data.get('calidad'),
            'observaciones': data.get('observaciones'),
            'equipos_usados': data.get('equipos_usados', []),
            'eficiencia_produccion': float(data.get('eficiencia_produccion', 0)),
            'costo_por_m3': float(data.get('costo_por_m3', 0)),
            'duracion_produccion': float(data.get('duracion_produccion', 0)),
            'activo': data.get('activo', True),
            'created_at': data.get('created_at', ''),
            'updated_at': data.get('updated_at', ''),
            # Campos en camelCase para compatibilidad con frontend
            'codigoLote': data.get('codigo_lote', ''),
            'fecha': data.get('fecha_produccion', ''),
            'fechaProduccion': data.get('fecha_produccion', ''),
            'horaInicio': data.get('hora_inicio_produccion', ''),
            'horaInicioProduccion': data.get('hora_inicio_produccion', ''),
            'horaFin': data.get('hora_fin_produccion'),
            'horaFinProduccion': data.get('hora_fin_produccion'),
            'volumenPlanificado': float(data.get('volumen_planificado_m3', 0)),
            'volumenPlanificadoM3': float(data.get('volumen_planificado_m3', 0)),
            'volumenProducido': float(data.get('volumen_producido_m3', 0)),
            'volumenProducidoM3': float(data.get('volumen_producido_m3', 0)),
            'costoTotal': float(data.get('costo_total_q', 0)),
            'costoTotalQ': float(data.get('costo_total_q', 0)),
            'equiposUsados': data.get('equipos_usados', []),
        }


class ProduccionPiedrineraListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar producción de piedrinera
    """
    agregado_nombre = serializers.CharField(source='agregado.nombre', read_only=True)
    supervisor_nombre = serializers.SerializerMethodField()
    operador_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = ProduccionPiedrinera
        fields = (
            'id', 'codigo_lote', 'fecha_produccion',
            'agregado_nombre', 'volumen_planificado_m3', 'volumen_producido_m3',
            'estado', 'estado_display', 'calidad',
            'supervisor_nombre', 'operador_nombre'
        )

    def get_supervisor_nombre(self, obj):
        if obj.supervisor:
            return f"{obj.supervisor.nombres} {obj.supervisor.apellidos}"
        return None

    def get_operador_nombre(self, obj):
        if obj.operador:
            return f"{obj.operador.nombres} {obj.operador.apellidos}"
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigo_lote': data.get('codigo_lote', ''),
            'fecha': data.get('fecha_produccion', ''),
            'fecha_produccion': data.get('fecha_produccion', ''),
            'agregado': data.get('agregado_nombre', ''),
            'agregado_nombre': data.get('agregado_nombre', ''),
            'volumen_planificado_m3': float(data.get('volumen_planificado_m3', 0)),
            'volumen_producido_m3': float(data.get('volumen_producido_m3', 0)),
            'volumenPlanificado': float(data.get('volumen_planificado_m3', 0)),
            'volumenProducido': float(data.get('volumen_producido_m3', 0)),
            'estado': data.get('estado', ''),
            'estado_display': data.get('estado_display', ''),
            'calidad': data.get('calidad'),
            'supervisor_nombre': data.get('supervisor_nombre'),
            'operador': data.get('operador_nombre'),
            'operador_nombre': data.get('operador_nombre'),
        }

