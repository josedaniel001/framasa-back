# Serializers del módulo Taller

from rest_framework import serializers
from .models import (
    Maquinaria, TipoMaquinaria, OrdenTrabajo,
    TipoMantenimiento, PrioridadOrden, EstadoOrden,
    OrdenTrabajoProducto
)
from planillas.models import Empleado


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


class OrdenTrabajoProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para productos de una orden de trabajo
    """
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    producto_unidad_medida = serializers.SerializerMethodField()
    producto_stock_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdenTrabajoProducto
        fields = (
            'id', 'orden_trabajo', 'producto',
            'producto_nombre', 'producto_codigo', 'producto_unidad_medida', 'producto_stock_actual',
            'cantidad', 'precio_unitario', 'costo_total',
            'descontado_inventario', 'movimiento_inventario',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'costo_total', 'created_at', 'updated_at')
    
    def get_producto_unidad_medida(self, obj):
        if obj.producto and hasattr(obj.producto, 'unidad_medida'):
            um = obj.producto.unidad_medida
            return um.nombre if hasattr(um, 'nombre') else str(um)
        return ""
    
    def get_producto_stock_actual(self, obj):
        if obj.producto:
            return obj.producto.stock_actual
        return 0
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': data.get('id'),
            'ordenTrabajoId': data.get('orden_trabajo'),
            'orden_trabajo_id': data.get('orden_trabajo'),
            'productoId': data.get('producto'),
            'producto_id': data.get('producto'),
            'productoNombre': data.get('producto_nombre', ''),
            'producto_nombre': data.get('producto_nombre', ''),
            'productoCodigo': data.get('producto_codigo', ''),
            'producto_codigo': data.get('producto_codigo', ''),
            'productoUnidadMedida': data.get('producto_unidad_medida', ''),
            'producto_unidad_medida': data.get('producto_unidad_medida', ''),
            'productoStockActual': data.get('producto_stock_actual', 0),
            'producto_stock_actual': data.get('producto_stock_actual', 0),
            'cantidad': data.get('cantidad', 0),
            'precioUnitario': float(data.get('precio_unitario', 0)) if data.get('precio_unitario') else None,
            'precio_unitario': float(data.get('precio_unitario', 0)) if data.get('precio_unitario') else None,
            'costoTotal': float(data.get('costo_total', 0)) if data.get('costo_total') else None,
            'costo_total': float(data.get('costo_total', 0)) if data.get('costo_total') else None,
            'descontadoInventario': data.get('descontado_inventario', False),
            'descontado_inventario': data.get('descontado_inventario', False),
            'movimientoInventarioId': data.get('movimiento_inventario'),
            'movimiento_inventario_id': data.get('movimiento_inventario'),
            'createdAt': data.get('created_at', ''),
            'created_at': data.get('created_at', ''),
            'updatedAt': data.get('updated_at', ''),
            'updated_at': data.get('updated_at', ''),
        }


class OrdenTrabajoSerializer(serializers.ModelSerializer):
    """
    Serializer para Orden de Trabajo con información completa
    """
    tipo_mantenimiento_display = serializers.CharField(
        source='get_tipo_mantenimiento_display', read_only=True
    )
    prioridad_display = serializers.CharField(
        source='get_prioridad_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    maquinaria_nombre = serializers.CharField(
        source='maquinaria.nombre', read_only=True
    )
    maquinaria_codigo = serializers.CharField(
        source='maquinaria.codigo', read_only=True
    )
    tecnico_nombre = serializers.SerializerMethodField()
    creado_por_nombre = serializers.SerializerMethodField()
    esta_vencida = serializers.BooleanField(read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)
    productos_orden = OrdenTrabajoProductoSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrdenTrabajo
        fields = (
            'id', 'codigo_orden',
            'maquinaria', 'maquinaria_nombre', 'maquinaria_codigo',
            'tecnico', 'tecnico_nombre',
            'creado_por', 'creado_por_nombre',
            'tipo_mantenimiento', 'tipo_mantenimiento_display',
            'descripcion_trabajo',
            'prioridad', 'prioridad_display',
            'observaciones',
            'repuestos_externos',
            'fecha_creacion_orden', 'fecha_inicio',
            'fecha_estimada_terminacion', 'fecha_terminacion_real',
            'estado', 'estado_display',
            'progreso', 'costo_estimado', 'costo_real',
            'activo', 'esta_vencida', 'dias_restantes',
            'productos_orden',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'codigo_orden', 'creado_por', 'created_at', 'updated_at',
            'maquinaria_nombre', 'maquinaria_codigo', 'tecnico_nombre',
            'creado_por_nombre', 'tipo_mantenimiento_display',
            'prioridad_display', 'estado_display', 'esta_vencida', 'dias_restantes'
        )
    
    def get_tecnico_nombre(self, obj):
        if obj.tecnico:
            return obj.tecnico.nombre_completo
        return None
    
    def get_creado_por_nombre(self, obj):
        if obj.creado_por:
            return obj.creado_por.get_full_name() or obj.creado_por.username
        return None
    
    def create(self, validated_data):
        # Asignar usuario que crea la orden
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['creado_por'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Personalizar la representación para que coincida con el formato esperado por el frontend
        """
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigoOrden': data.get('codigo_orden', ''),
            'codigo_orden': data.get('codigo_orden', ''),
            # Maquinaria
            'maquinariaId': data.get('maquinaria'),
            'maquinaria_id': data.get('maquinaria'),
            'maquinariaNombre': data.get('maquinaria_nombre', ''),
            'maquinaria_nombre': data.get('maquinaria_nombre', ''),
            'maquinariaCodigo': data.get('maquinaria_codigo', ''),
            'maquinaria_codigo': data.get('maquinaria_codigo', ''),
            'equipo': f"{data.get('maquinaria_codigo', '')} - {data.get('maquinaria_nombre', '')}",
            # Técnico
            'tecnicoId': data.get('tecnico'),
            'tecnico_id': data.get('tecnico'),
            'tecnicoNombre': data.get('tecnico_nombre', ''),
            'tecnico_nombre': data.get('tecnico_nombre', ''),
            'tecnico': data.get('tecnico_nombre', ''),
            # Creado por
            'creadoPorId': data.get('creado_por'),
            'creado_por_id': data.get('creado_por'),
            'creadoPorNombre': data.get('creado_por_nombre', ''),
            'creado_por_nombre': data.get('creado_por_nombre', ''),
            # Tipo mantenimiento
            'tipoMantenimiento': data.get('tipo_mantenimiento', ''),
            'tipo_mantenimiento': data.get('tipo_mantenimiento', ''),
            'tipoMantenimientoDisplay': data.get('tipo_mantenimiento_display', ''),
            'tipo_mantenimiento_display': data.get('tipo_mantenimiento_display', ''),
            'tipo': data.get('tipo_mantenimiento_display', ''),
            # Descripción
            'descripcionTrabajo': data.get('descripcion_trabajo', ''),
            'descripcion_trabajo': data.get('descripcion_trabajo', ''),
            'descripcion': data.get('descripcion_trabajo', ''),
            # Prioridad
            'prioridad': data.get('prioridad', ''),
            'prioridadDisplay': data.get('prioridad_display', ''),
            'prioridad_display': data.get('prioridad_display', ''),
            # Observaciones
            'observaciones': data.get('observaciones', ''),
            # Repuestos externos
            'repuestosExternos': data.get('repuestos_externos', []),
            'repuestos_externos': data.get('repuestos_externos', []),
            # Productos de ferretería (materiales)
            'productosOrden': data.get('productos_orden', []),
            'productos_orden': data.get('productos_orden', []),
            # Fechas
            'fechaCreacionOrden': data.get('fecha_creacion_orden', ''),
            'fecha_creacion_orden': data.get('fecha_creacion_orden', ''),
            'fechaCreacion': data.get('fecha_creacion_orden', ''),
            'fechaInicio': data.get('fecha_inicio', ''),
            'fecha_inicio': data.get('fecha_inicio', ''),
            'fechaEstimadaTerminacion': data.get('fecha_estimada_terminacion', ''),
            'fecha_estimada_terminacion': data.get('fecha_estimada_terminacion', ''),
            'fechaTerminacionReal': data.get('fecha_terminacion_real'),
            'fecha_terminacion_real': data.get('fecha_terminacion_real'),
            # Estado
            'estado': data.get('estado', ''),
            'estadoDisplay': data.get('estado_display', ''),
            'estado_display': data.get('estado_display', ''),
            # Progreso y costos
            'progreso': data.get('progreso', 0),
            'costoEstimado': float(data.get('costo_estimado', 0)),
            'costo_estimado': float(data.get('costo_estimado', 0)),
            'costoReal': float(data.get('costo_real', 0)) if data.get('costo_real') is not None else None,
            'costo_real': float(data.get('costo_real', 0)) if data.get('costo_real') is not None else None,
            # Compatibilidad con frontend existente
            'costoTotalQ': float(data.get('costo_estimado', 0)),
            'costo_total_q': float(data.get('costo_estimado', 0)),
            'costo': float(data.get('costo_estimado', 0)),
            # Control
            'activo': data.get('activo', True),
            'estaVencida': data.get('esta_vencida', False),
            'esta_vencida': data.get('esta_vencida', False),
            'diasRestantes': data.get('dias_restantes', 0),
            'dias_restantes': data.get('dias_restantes', 0),
            # Timestamps
            'createdAt': data.get('created_at', ''),
            'created_at': data.get('created_at', ''),
            'updatedAt': data.get('updated_at', ''),
            'updated_at': data.get('updated_at', ''),
        }


class OrdenTrabajoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar órdenes de trabajo
    """
    tipo_mantenimiento_display = serializers.CharField(
        source='get_tipo_mantenimiento_display', read_only=True
    )
    prioridad_display = serializers.CharField(
        source='get_prioridad_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    maquinaria_nombre = serializers.CharField(
        source='maquinaria.nombre', read_only=True
    )
    tecnico_nombre = serializers.SerializerMethodField()
    esta_vencida = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = OrdenTrabajo
        fields = (
            'id', 'codigo_orden',
            'maquinaria', 'maquinaria_nombre',
            'tecnico', 'tecnico_nombre',
            'tipo_mantenimiento', 'tipo_mantenimiento_display',
            'descripcion_trabajo',
            'prioridad', 'prioridad_display',
            'fecha_creacion_orden', 'fecha_inicio',
            'fecha_estimada_terminacion',
            'estado', 'estado_display',
            'progreso', 'costo_estimado', 'costo_real',
            'activo', 'esta_vencida'
        )
    
    def get_tecnico_nombre(self, obj):
        if obj.tecnico:
            return obj.tecnico.nombre_completo
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': str(data.get('id', '')),
            'codigoOrden': data.get('codigo_orden', ''),
            'equipo': data.get('maquinaria_nombre', ''),
            'tecnico': data.get('tecnico_nombre', ''),
            'tipo': data.get('tipo_mantenimiento_display', ''),
            'descripcion': data.get('descripcion_trabajo', ''),
            'prioridad': data.get('prioridad_display', ''),
            'prioridadValor': data.get('prioridad', ''),
            'fechaCreacion': data.get('fecha_creacion_orden', ''),
            'fechaInicio': data.get('fecha_inicio', ''),
            'fechaEstimadaTerminacion': data.get('fecha_estimada_terminacion', ''),
            'estado': data.get('estado_display', ''),
            'estadoValor': data.get('estado', ''),
            'progreso': data.get('progreso', 0),
            'costoEstimado': float(data.get('costo_estimado', 0)),
            'costoReal': float(data.get('costo_real', 0)) if data.get('costo_real') is not None else None,
            'costo': float(data.get('costo_estimado', 0)),
            'activo': data.get('activo', True),
            'estaVencida': data.get('esta_vencida', False),
        }


class OrdenTrabajoCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar órdenes de trabajo
    """
    codigo_orden = serializers.CharField(required=False, allow_blank=True, max_length=20)
    # Campo para compatibilidad con frontend que envía costo_total_q
    costo_total_q = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, write_only=True
    )
    # Campo para recibir materiales desde el frontend
    materiales = serializers.ListField(
        child=serializers.DictField(), required=False, write_only=True
    )
    
    class Meta:
        model = OrdenTrabajo
        fields = (
            'codigo_orden',
            'maquinaria', 'tecnico',
            'tipo_mantenimiento', 'descripcion_trabajo',
            'prioridad', 'observaciones',
            'repuestos_externos',
            'fecha_creacion_orden', 'fecha_inicio',
            'fecha_estimada_terminacion', 'fecha_terminacion_real',
            'estado', 'progreso', 'costo_estimado', 'costo_real', 'costo_total_q', 'activo',
            'materiales'
        )
    
    def to_internal_value(self, data):
        """Mapear costo_total_q a costo_estimado para compatibilidad con frontend"""
        # Si viene costo_total_q y no viene costo_estimado, usarlo
        if 'costo_total_q' in data and 'costo_estimado' not in data:
            data = data.copy() if hasattr(data, 'copy') else dict(data)
            data['costo_estimado'] = data.pop('costo_total_q')
        return super().to_internal_value(data)
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar que fecha_inicio <= fecha_estimada_terminacion
        fecha_inicio = data.get('fecha_inicio')
        fecha_estimada = data.get('fecha_estimada_terminacion')
        
        if fecha_inicio and fecha_estimada and fecha_inicio > fecha_estimada:
            raise serializers.ValidationError({
                'fecha_estimada_terminacion': 'La fecha estimada de terminación debe ser igual o posterior a la fecha de inicio.'
            })
        
        # Validar progreso
        progreso = data.get('progreso', 0)
        if progreso < 0 or progreso > 100:
            raise serializers.ValidationError({
                'progreso': 'El progreso debe estar entre 0 y 100.'
            })
        
        return data
    
    def create(self, validated_data):
        # Extraer materiales antes de crear la orden
        materiales_data = validated_data.pop('materiales', [])
        
        # Asignar usuario que crea la orden
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['creado_por'] = request.user
        
        # Si no se proporciona código, el modelo lo generará automáticamente
        codigo = validated_data.get('codigo_orden', '')
        if not codigo or codigo.strip() == '':
            validated_data.pop('codigo_orden', None)
        
        # Crear la orden
        orden = super().create(validated_data)
        
        # Crear los productos de la orden
        self._crear_productos_orden(orden, materiales_data, request)
        
        return orden
    
    def update(self, instance, validated_data):
        # Extraer materiales antes de actualizar la orden
        materiales_data = validated_data.pop('materiales', None)
        
        # Actualizar la orden
        orden = super().update(instance, validated_data)
        
        # Si se enviaron materiales, actualizar los productos de la orden
        if materiales_data is not None:
            request = self.context.get('request')
            self._actualizar_productos_orden(orden, materiales_data, request)
        
        return orden
    
    def _crear_productos_orden(self, orden, materiales_data, request):
        """Crear productos para una orden nueva"""
        from ferreteria.models import Producto, MovimientoInventario
        
        for material in materiales_data:
            producto_id = material.get('producto_id')
            cantidad = material.get('cantidad', 1)
            
            if not producto_id:
                continue
            
            try:
                producto = Producto.objects.get(id=producto_id)
                
                # Crear el registro del producto en la orden
                orden_producto = OrdenTrabajoProducto.objects.create(
                    orden_trabajo=orden,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.costo_unitario,
                    descontado_inventario=False
                )
                
                # Crear movimiento de inventario (salida)
                if request and request.user.is_authenticated:
                    movimiento = MovimientoInventario.objects.create(
                        producto=producto,
                        usuario=request.user,
                        tipo='SALIDA',
                        cantidad=cantidad,
                        motivo=f'Uso en Orden de Taller: {orden.codigo_orden}',
                        observaciones=f'Salida automática por orden de trabajo {orden.codigo_orden}'
                    )
                    
                    # Actualizar el registro del producto con la referencia al movimiento
                    orden_producto.movimiento_inventario = movimiento
                    orden_producto.descontado_inventario = True
                    orden_producto.save()
                    
            except Producto.DoesNotExist:
                continue
    
    def _actualizar_productos_orden(self, orden, materiales_data, request):
        """Actualizar productos de una orden existente"""
        from ferreteria.models import Producto, MovimientoInventario
        
        # Obtener productos actuales en la orden (como diccionario producto_id -> orden_producto)
        productos_actuales = {
            op.producto_id: op for op in orden.productos_orden.all()
        }
        
        # Crear diccionario de materiales nuevos (producto_id -> cantidad)
        materiales_dict = {}
        for material in materiales_data:
            producto_id = material.get('producto_id')
            cantidad = material.get('cantidad', 1)
            if producto_id:
                materiales_dict[int(producto_id)] = cantidad
        
        productos_actuales_ids = set(productos_actuales.keys())
        productos_nuevos_ids = set(materiales_dict.keys())
        
        # Productos a agregar (están en la nueva lista pero no en la actual)
        productos_a_agregar = productos_nuevos_ids - productos_actuales_ids
        
        # Productos a eliminar (están en la actual pero no en la nueva)
        productos_a_eliminar = productos_actuales_ids - productos_nuevos_ids
        
        # Productos que permanecen (pueden tener cambio de cantidad)
        productos_a_actualizar = productos_actuales_ids & productos_nuevos_ids
        
        # 1. Agregar nuevos productos
        for producto_id in productos_a_agregar:
            cantidad = materiales_dict[producto_id]
            try:
                producto = Producto.objects.get(id=producto_id)
                
                orden_producto = OrdenTrabajoProducto.objects.create(
                    orden_trabajo=orden,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.costo_unitario,
                    descontado_inventario=False
                )
                
                if request and request.user.is_authenticated:
                    movimiento = MovimientoInventario.objects.create(
                        producto=producto,
                        usuario=request.user,
                        tipo='SALIDA',
                        cantidad=cantidad,
                        motivo=f'Uso en Orden de Taller: {orden.codigo_orden}',
                        observaciones=f'Salida automática por orden de trabajo {orden.codigo_orden}'
                    )
                    orden_producto.movimiento_inventario = movimiento
                    orden_producto.descontado_inventario = True
                    orden_producto.save()
                    
            except Producto.DoesNotExist:
                continue
        
        # 2. Actualizar cantidades de productos existentes
        for producto_id in productos_a_actualizar:
            orden_producto = productos_actuales[producto_id]
            nueva_cantidad = materiales_dict[producto_id]
            cantidad_anterior = orden_producto.cantidad
            
            if nueva_cantidad != cantidad_anterior:
                diferencia = nueva_cantidad - cantidad_anterior
                
                # Actualizar la cantidad en el registro
                orden_producto.cantidad = nueva_cantidad
                orden_producto.costo_total = (orden_producto.precio_unitario or 0) * nueva_cantidad
                orden_producto.save()
                
                # Crear movimiento de inventario por la diferencia
                if request and request.user.is_authenticated and diferencia != 0:
                    try:
                        producto = Producto.objects.get(id=producto_id)
                        
                        if diferencia > 0:
                            # Se necesita más cantidad -> SALIDA adicional
                            MovimientoInventario.objects.create(
                                producto=producto,
                                usuario=request.user,
                                tipo='SALIDA',
                                cantidad=diferencia,
                                motivo=f'Ajuste en Orden de Taller: {orden.codigo_orden}',
                                observaciones=f'Aumento de cantidad de {cantidad_anterior} a {nueva_cantidad} en orden {orden.codigo_orden}'
                            )
                        else:
                            # Se necesita menos cantidad -> ENTRADA (devolución)
                            MovimientoInventario.objects.create(
                                producto=producto,
                                usuario=request.user,
                                tipo='ENTRADA',
                                cantidad=abs(diferencia),
                                motivo=f'Devolución por ajuste en Orden de Taller: {orden.codigo_orden}',
                                observaciones=f'Reducción de cantidad de {cantidad_anterior} a {nueva_cantidad} en orden {orden.codigo_orden}'
                            )
                    except Producto.DoesNotExist:
                        continue
        
        # 3. Eliminar productos que ya no están en la lista (devolver al inventario)
        for producto_id in productos_a_eliminar:
            orden_producto = productos_actuales[producto_id]
            cantidad_devolver = orden_producto.cantidad
            
            # Crear movimiento de entrada (devolución) si ya se había descontado
            if orden_producto.descontado_inventario and request and request.user.is_authenticated:
                try:
                    producto = Producto.objects.get(id=producto_id)
                    MovimientoInventario.objects.create(
                        producto=producto,
                        usuario=request.user,
                        tipo='ENTRADA',
                        cantidad=cantidad_devolver,
                        motivo=f'Devolución por eliminación en Orden de Taller: {orden.codigo_orden}',
                        observaciones=f'Producto eliminado de la orden de trabajo {orden.codigo_orden}'
                    )
                except Producto.DoesNotExist:
                    pass
            
            # Eliminar el registro del producto
            orden_producto.delete()
