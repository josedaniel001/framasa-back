from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import (
    Factura, DetalleFactura, Pago, EstadoFactura, TipoPago, EmpresaFactura,
    Cotizacion, DetalleCotizacion, EstadoCotizacion
)
from ferreteria.models import Producto, Cliente
from bloquera.models import ProductoBloquera
from piedrinera.models import AgregadoPiedrinera
from decimal import Decimal


class DetalleFacturaSerializer(serializers.ModelSerializer):
    """Serializer para detalles de factura"""
    producto_id = serializers.IntegerField(write_only=True, required=True)
    producto_empresa = serializers.ChoiceField(choices=EmpresaFactura.choices, write_only=True, required=True)
    producto_codigo = serializers.CharField(read_only=True)
    producto_nombre = serializers.CharField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = DetalleFactura
        fields = (
            'id', 'factura', 'producto_id', 'producto_empresa',
            'producto_codigo', 'producto_nombre',
            'cantidad', 'precio_unitario', 'descuento', 'subtotal',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'factura', 'producto_codigo', 'producto_nombre', 'subtotal', 'created_at', 'updated_at')
    
    def validate(self, data):
        """Validar que el producto existe y tiene stock"""
        producto_id = data.get('producto_id')
        empresa = data.get('producto_empresa')
        cantidad = data.get('cantidad')
        
        # Obtener el modelo según la empresa
        if empresa == EmpresaFactura.FERRETERIA:
            try:
                producto = Producto.objects.get(id=producto_id, activo=True)
                if producto.stock_actual < int(cantidad):
                    raise serializers.ValidationError({
                        'cantidad': f'Stock insuficiente. Stock disponible: {producto.stock_actual}'
                    })
            except Producto.DoesNotExist:
                raise serializers.ValidationError({
                    'producto_id': 'Producto no encontrado o inactivo'
                })
        elif empresa == EmpresaFactura.BLOQUERA:
            try:
                producto = ProductoBloquera.objects.get(id=producto_id, activo=True)
                if producto.stock_actual < int(cantidad):
                    raise serializers.ValidationError({
                        'cantidad': f'Stock insuficiente. Stock disponible: {producto.stock_actual}'
                    })
            except ProductoBloquera.DoesNotExist:
                raise serializers.ValidationError({
                    'producto_id': 'Producto no encontrado o inactivo'
                })
        elif empresa == EmpresaFactura.PIEDRINERA:
            try:
                producto = AgregadoPiedrinera.objects.get(id=producto_id, activo=True)
                if producto.stock_actual_m3 < Decimal(str(cantidad)):
                    raise serializers.ValidationError({
                        'cantidad': f'Stock insuficiente. Stock disponible: {producto.stock_actual_m3} m³'
                    })
            except AgregadoPiedrinera.DoesNotExist:
                raise serializers.ValidationError({
                    'producto_id': 'Producto no encontrado o inactivo'
                })
        
        return data
    
    def create(self, validated_data):
        """Crear detalle y actualizar información del producto"""
        producto_id = validated_data.pop('producto_id')
        empresa = validated_data.pop('producto_empresa')
        
        # Obtener el ContentType según la empresa
        if empresa == EmpresaFactura.FERRETERIA:
            content_type = ContentType.objects.get_for_model(Producto)
            producto = Producto.objects.get(id=producto_id)
        elif empresa == EmpresaFactura.BLOQUERA:
            content_type = ContentType.objects.get_for_model(ProductoBloquera)
            producto = ProductoBloquera.objects.get(id=producto_id)
        elif empresa == EmpresaFactura.PIEDRINERA:
            content_type = ContentType.objects.get_for_model(AgregadoPiedrinera)
            producto = AgregadoPiedrinera.objects.get(id=producto_id)
        
        # Guardar información del producto al momento de la venta
        validated_data['content_type'] = content_type
        validated_data['object_id'] = producto_id
        validated_data['producto_codigo'] = producto.codigo
        validated_data['producto_nombre'] = producto.nombre
        validated_data['producto_empresa'] = empresa
        
        return super().create(validated_data)


class PagoSerializer(serializers.ModelSerializer):
    """Serializer para pagos"""
    tipo_pago_display = serializers.CharField(source='get_tipo_pago_display', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = Pago
        fields = (
            'id', 'factura', 'factura_id', 'tipo_pago', 'tipo_pago_display',
            'monto', 'referencia', 'observaciones',
            'usuario', 'usuario_id', 'usuario_nombre',
            'fecha_pago', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'usuario_nombre', 'created_at', 'updated_at')
    
    def validate(self, data):
        """Validar el pago"""
        factura = data.get('factura')
        monto = data.get('monto')
        tipo_pago = data.get('tipo_pago')
        
        if not factura:
            raise serializers.ValidationError({'factura': 'La factura es requerida'})
        
        # Validar que el monto no exceda el saldo pendiente
        saldo_pendiente = factura.saldo_pendiente
        if monto > saldo_pendiente:
            raise serializers.ValidationError({
                'monto': f'El monto excede el saldo pendiente. Saldo: Q{saldo_pendiente:.2f}'
            })
        
        # Validar fiado
        if tipo_pago == TipoPago.FIADO:
            puede, mensaje = factura.puede_pagar_fiado(monto)
            if not puede:
                raise serializers.ValidationError({'tipo_pago': mensaje})
        
        return data
    
    def create(self, validated_data):
        """Asignar usuario automáticamente"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        return super().create(validated_data)


class FacturaSerializer(serializers.ModelSerializer):
    """Serializer para facturas"""
    detalles = DetalleFacturaSerializer(many=True, read_only=True)
    pagos = PagoSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_nit = serializers.CharField(source='cliente.nit', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    empresa_display = serializers.CharField(source='get_empresa_display', read_only=True)
    
    class Meta:
        model = Factura
        fields = (
            'id', 'numero_factura', 'empresa', 'empresa_display',
            'cliente', 'cliente_id', 'cliente_nombre', 'cliente_nit',
            'subtotal', 'descuento', 'total',
            'total_pagado', 'saldo_pendiente',
            'estado', 'estado_display',
            'observaciones',
            'usuario', 'usuario_id', 'usuario_nombre',
            'fecha_factura', 'fecha_vencimiento',
            'detalles', 'pagos',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'numero_factura', 'subtotal', 'total',
            'total_pagado', 'saldo_pendiente', 'estado',
            'created_at', 'updated_at'
        )
    
    def create(self, validated_data):
        """Crear factura con número automático y asignar usuario"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        
        # Generar número de factura automático
        if not validated_data.get('numero_factura'):
            empresa = validated_data.get('empresa')
            prefijo = {
                EmpresaFactura.FERRETERIA: 'FERR',
                EmpresaFactura.BLOQUERA: 'BLOQ',
                EmpresaFactura.PIEDRINERA: 'PIED',
                EmpresaFactura.MIXTA: 'MIXT'
            }.get(empresa, 'FACT')
            
            # Obtener el último número de factura
            ultima_factura = Factura.objects.filter(
                numero_factura__startswith=prefijo
            ).order_by('-numero_factura').first()
            
            if ultima_factura:
                try:
                    ultimo_numero = int(ultima_factura.numero_factura.replace(prefijo, ''))
                    nuevo_numero = ultimo_numero + 1
                except ValueError:
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            validated_data['numero_factura'] = f"{prefijo}{nuevo_numero:06d}"
        
        return super().create(validated_data)


class FacturaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear facturas con detalles"""
    detalles = DetalleFacturaSerializer(many=True, write_only=True)
    
    class Meta:
        model = Factura
        fields = (
            'empresa', 'cliente', 'descuento', 'observaciones',
            'fecha_vencimiento', 'detalles'
        )
    
    def validate(self, data):
        """Validar que si hay productos de múltiples empresas, se use empresa MIXTA"""
        detalles = data.get('detalles', [])
        if detalles:
            empresas_en_detalles = set(det.get('producto_empresa') for det in detalles)
            if len(empresas_en_detalles) > 1:
                # Si hay productos de múltiples empresas, forzar empresa MIXTA
                data['empresa'] = EmpresaFactura.MIXTA
            elif len(empresas_en_detalles) == 1:
                # Si todos los productos son de una empresa, usar esa empresa
                empresa_productos = empresas_en_detalles.pop()
                if data.get('empresa') != empresa_productos:
                    data['empresa'] = empresa_productos
        return data
    
    def create(self, validated_data):
        """Crear factura con detalles y actualizar stock"""
        detalles_data = validated_data.pop('detalles')
        request = self.context.get('request')
        
        # Asignar usuario
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        
        # Generar número de factura
        empresa = validated_data.get('empresa')
        
        # Si hay productos de múltiples empresas, usar prefijo MIXT
        empresas_en_detalles = set(det['producto_empresa'] for det in detalles_data)
        if len(empresas_en_detalles) > 1:
            prefijo = 'MIXT'
            validated_data['empresa'] = EmpresaFactura.MIXTA
        else:
            prefijo = {
                EmpresaFactura.FERRETERIA: 'FERR',
                EmpresaFactura.BLOQUERA: 'BLOQ',
                EmpresaFactura.PIEDRINERA: 'PIED',
                EmpresaFactura.MIXTA: 'MIXT'
            }.get(empresa, 'FACT')
        
        ultima_factura = Factura.objects.filter(
            numero_factura__startswith=prefijo
        ).order_by('-numero_factura').first()
        
        if ultima_factura:
            try:
                ultimo_numero = int(ultima_factura.numero_factura.replace(prefijo, ''))
                nuevo_numero = ultimo_numero + 1
            except ValueError:
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        
        validated_data['numero_factura'] = f"{prefijo}{nuevo_numero:06d}"
        validated_data['estado'] = EstadoFactura.PENDIENTE
        
        # Crear factura
        factura = Factura.objects.create(**validated_data)
        
        # Crear detalles y actualizar stock
        for detalle_data in detalles_data:
            producto_id = detalle_data['producto_id']
            empresa_prod = detalle_data['producto_empresa']
            cantidad = detalle_data['cantidad']
            
            # Obtener producto y actualizar stock
            if empresa_prod == EmpresaFactura.FERRETERIA:
                producto = Producto.objects.get(id=producto_id)
                content_type = ContentType.objects.get_for_model(Producto)
                # Crear movimiento de inventario
                from ferreteria.models import MovimientoInventario, TipoMovimiento
                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo=TipoMovimiento.SALIDA,
                    cantidad=int(cantidad),
                    motivo=f"Venta - Factura {factura.numero_factura}",
                    usuario=request.user
                )
            elif empresa_prod == EmpresaFactura.BLOQUERA:
                producto = ProductoBloquera.objects.get(id=producto_id)
                content_type = ContentType.objects.get_for_model(ProductoBloquera)
                from bloquera.models import MovimientoInventarioBloquera, TipoMovimientoBloquera
                MovimientoInventarioBloquera.objects.create(
                    producto=producto,
                    tipo=TipoMovimientoBloquera.SALIDA,
                    cantidad=int(cantidad),
                    motivo=f"Venta - Factura {factura.numero_factura}",
                    usuario=request.user
                )
            elif empresa_prod == EmpresaFactura.PIEDRINERA:
                producto = AgregadoPiedrinera.objects.get(id=producto_id)
                content_type = ContentType.objects.get_for_model(AgregadoPiedrinera)
                from piedrinera.models import MovimientoInventarioPiedrinera, TipoMovimientoPiedrinera
                MovimientoInventarioPiedrinera.objects.create(
                    producto=producto,
                    tipo=TipoMovimientoPiedrinera.SALIDA,
                    cantidad=Decimal(str(cantidad)),
                    motivo=f"Venta - Factura {factura.numero_factura}",
                    usuario=request.user
                )
            
            # Obtener precio del producto si no se proporciona
            precio_unitario = detalle_data.get('precio_unitario')
            if not precio_unitario:
                if empresa_prod == EmpresaFactura.FERRETERIA:
                    precio_unitario = producto.precio_venta
                elif empresa_prod == EmpresaFactura.BLOQUERA:
                    precio_unitario = producto.precio_unitario
                elif empresa_prod == EmpresaFactura.PIEDRINERA:
                    precio_unitario = producto.precio_venta_m3
            
            # Crear detalle
            DetalleFactura.objects.create(
                factura=factura,
                content_type=content_type,
                object_id=producto_id,
                producto_codigo=producto.codigo,
                producto_nombre=producto.nombre,
                producto_empresa=empresa_prod,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                descuento=detalle_data.get('descuento', 0)
            )
        
        # Calcular totales
        factura.calcular_totales()
        
        return factura


class DetalleCotizacionSerializer(serializers.ModelSerializer):
    """Serializer para detalles de cotización"""
    producto_id = serializers.IntegerField(write_only=True, required=True)
    producto_empresa = serializers.ChoiceField(choices=EmpresaFactura.choices, write_only=True, required=True)
    producto_codigo = serializers.CharField(read_only=True)
    producto_nombre = serializers.CharField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = DetalleCotizacion
        fields = (
            'id', 'cotizacion', 'producto_id', 'producto_empresa',
            'producto_codigo', 'producto_nombre',
            'cantidad', 'precio_unitario', 'descuento', 'subtotal',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'cotizacion', 'producto_codigo', 'producto_nombre', 'subtotal', 'created_at', 'updated_at')
    
    def validate(self, data):
        """Validar que el producto existe"""
        producto_id = data.get('producto_id')
        empresa = data.get('producto_empresa')
        
        # Obtener el modelo según la empresa
        if empresa == EmpresaFactura.FERRETERIA:
            try:
                Producto.objects.get(id=producto_id, activo=True)
            except Producto.DoesNotExist:
                raise serializers.ValidationError({
                    'producto_id': 'Producto no encontrado o inactivo'
                })
        elif empresa == EmpresaFactura.BLOQUERA:
            try:
                ProductoBloquera.objects.get(id=producto_id, activo=True)
            except ProductoBloquera.DoesNotExist:
                raise serializers.ValidationError({
                    'producto_id': 'Producto no encontrado o inactivo'
                })
        elif empresa == EmpresaFactura.PIEDRINERA:
            try:
                AgregadoPiedrinera.objects.get(id=producto_id, activo=True)
            except AgregadoPiedrinera.DoesNotExist:
                raise serializers.ValidationError({
                    'producto_id': 'Producto no encontrado o inactivo'
                })
        
        return data
    
    def create(self, validated_data):
        """Crear detalle y guardar información del producto"""
        producto_id = validated_data.pop('producto_id')
        empresa = validated_data.pop('producto_empresa')
        
        # Obtener el ContentType según la empresa
        if empresa == EmpresaFactura.FERRETERIA:
            content_type = ContentType.objects.get_for_model(Producto)
            producto = Producto.objects.get(id=producto_id)
        elif empresa == EmpresaFactura.BLOQUERA:
            content_type = ContentType.objects.get_for_model(ProductoBloquera)
            producto = ProductoBloquera.objects.get(id=producto_id)
        elif empresa == EmpresaFactura.PIEDRINERA:
            content_type = ContentType.objects.get_for_model(AgregadoPiedrinera)
            producto = AgregadoPiedrinera.objects.get(id=producto_id)
        
        # Guardar información del producto al momento de la cotización
        validated_data['content_type'] = content_type
        validated_data['object_id'] = producto_id
        validated_data['producto_codigo'] = producto.codigo
        validated_data['producto_nombre'] = producto.nombre
        validated_data['producto_empresa'] = empresa
        
        return super().create(validated_data)


class CotizacionSerializer(serializers.ModelSerializer):
    """Serializer para cotizaciones"""
    detalles = DetalleCotizacionSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_nit = serializers.CharField(source='cliente.nit', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    empresa_display = serializers.CharField(source='get_empresa_display', read_only=True)
    factura_generada_numero = serializers.CharField(source='factura_generada.numero_factura', read_only=True)
    
    class Meta:
        model = Cotizacion
        fields = (
            'id', 'numero_cotizacion', 'empresa', 'empresa_display',
            'cliente', 'cliente_id', 'cliente_nombre', 'cliente_nit',
            'subtotal', 'descuento', 'total',
            'estado', 'estado_display',
            'observaciones', 'condiciones',
            'fecha_vencimiento', 'fecha_aceptacion', 'fecha_cotizacion',
            'factura_generada', 'factura_generada_numero',
            'usuario', 'usuario_id', 'usuario_nombre',
            'detalles',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'numero_cotizacion', 'subtotal', 'total',
            'estado', 'fecha_aceptacion', 'factura_generada',
            'created_at', 'updated_at'
        )


class CotizacionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear cotizaciones con detalles"""
    detalles = DetalleCotizacionSerializer(many=True, write_only=True)
    
    class Meta:
        model = Cotizacion
        fields = (
            'empresa', 'cliente', 'descuento', 'observaciones', 'condiciones',
            'fecha_vencimiento', 'detalles'
        )
    
    def validate(self, data):
        """Validar que si hay productos de múltiples empresas, se use empresa MIXTA"""
        detalles = data.get('detalles', [])
        if detalles:
            empresas_en_detalles = set(det.get('producto_empresa') for det in detalles)
            if len(empresas_en_detalles) > 1:
                data['empresa'] = EmpresaFactura.MIXTA
            elif len(empresas_en_detalles) == 1:
                empresa_productos = empresas_en_detalles.pop()
                if data.get('empresa') != empresa_productos:
                    data['empresa'] = empresa_productos
        return data
    
    def create(self, validated_data):
        """Crear cotización con detalles"""
        detalles_data = validated_data.pop('detalles')
        request = self.context.get('request')
        
        # Asignar usuario
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        
        # Generar número de cotización
        empresa = validated_data.get('empresa')
        
        # Si hay productos de múltiples empresas, usar prefijo MIXT
        empresas_en_detalles = set(det['producto_empresa'] for det in detalles_data)
        if len(empresas_en_detalles) > 1:
            prefijo = 'MIXT'
            validated_data['empresa'] = EmpresaFactura.MIXTA
        else:
            prefijo = {
                EmpresaFactura.FERRETERIA: 'COTF',
                EmpresaFactura.BLOQUERA: 'COTB',
                EmpresaFactura.PIEDRINERA: 'COTP',
                EmpresaFactura.MIXTA: 'COTM'
            }.get(empresa, 'COT')
        
        ultima_cotizacion = Cotizacion.objects.filter(
            numero_cotizacion__startswith=prefijo
        ).order_by('-numero_cotizacion').first()
        
        if ultima_cotizacion:
            try:
                ultimo_numero = int(ultima_cotizacion.numero_cotizacion.replace(prefijo, ''))
                nuevo_numero = ultimo_numero + 1
            except ValueError:
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        
        validated_data['numero_cotizacion'] = f"{prefijo}{nuevo_numero:06d}"
        validated_data['estado'] = EstadoCotizacion.BORRADOR
        
        # Crear cotización
        cotizacion = Cotizacion.objects.create(**validated_data)
        
        # Crear detalles
        for detalle_data in detalles_data:
            producto_id = detalle_data['producto_id']
            empresa_prod = detalle_data['producto_empresa']
            
            # Obtener producto
            if empresa_prod == EmpresaFactura.FERRETERIA:
                producto = Producto.objects.get(id=producto_id)
                content_type = ContentType.objects.get_for_model(Producto)
            elif empresa_prod == EmpresaFactura.BLOQUERA:
                producto = ProductoBloquera.objects.get(id=producto_id)
                content_type = ContentType.objects.get_for_model(ProductoBloquera)
            elif empresa_prod == EmpresaFactura.PIEDRINERA:
                producto = AgregadoPiedrinera.objects.get(id=producto_id)
                content_type = ContentType.objects.get_for_model(AgregadoPiedrinera)
            
            # Obtener precio del producto si no se proporciona
            precio_unitario = detalle_data.get('precio_unitario')
            if not precio_unitario:
                if empresa_prod == EmpresaFactura.FERRETERIA:
                    precio_unitario = producto.precio_venta
                elif empresa_prod == EmpresaFactura.BLOQUERA:
                    precio_unitario = producto.precio_unitario
                elif empresa_prod == EmpresaFactura.PIEDRINERA:
                    precio_unitario = producto.precio_venta_m3
            
            # Crear detalle
            DetalleCotizacion.objects.create(
                cotizacion=cotizacion,
                content_type=content_type,
                object_id=producto_id,
                producto_codigo=producto.codigo,
                producto_nombre=producto.nombre,
                producto_empresa=empresa_prod,
                cantidad=detalle_data['cantidad'],
                precio_unitario=precio_unitario,
                descuento=detalle_data.get('descuento', 0)
            )
        
        # Calcular totales
        cotizacion.calcular_totales()
        
        return cotizacion

