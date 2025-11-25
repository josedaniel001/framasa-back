from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from authentication.models import Usuario
from ferreteria.models import Cliente


class EstadoFactura(models.TextChoices):
    """Estados de una factura"""
    BORRADOR = 'BORRADOR', 'Borrador'
    PENDIENTE = 'PENDIENTE', 'Pendiente de Pago'
    PARCIAL = 'PARCIAL', 'Pago Parcial'
    PAGADA = 'PAGADA', 'Pagada'
    ANULADA = 'ANULADA', 'Anulada'


class EstadoCotizacion(models.TextChoices):
    """Estados de una cotización"""
    BORRADOR = 'BORRADOR', 'Borrador'
    ENVIADA = 'ENVIADA', 'Enviada al Cliente'
    ACEPTADA = 'ACEPTADA', 'Aceptada'
    RECHAZADA = 'RECHAZADA', 'Rechazada'
    VENCIDA = 'VENCIDA', 'Vencida'


class TipoPago(models.TextChoices):
    """Tipos de pago disponibles"""
    EFECTIVO = 'EFECTIVO', 'Efectivo'
    TARJETA = 'TARJETA', 'Tarjeta'
    FIADO = 'FIADO', 'Fiado'


class EmpresaFactura(models.TextChoices):
    """Empresas que pueden facturar"""
    FERRETERIA = 'FERRETERIA', 'Ferretería'
    BLOQUERA = 'BLOQUERA', 'Bloquera'
    PIEDRINERA = 'PIEDRINERA', 'Piedrinera'
    MIXTA = 'MIXTA', 'Mixta (Múltiples Empresas)'


class Factura(models.Model):
    """
    Modelo unificado para facturas de las tres empresas
    """
    numero_factura = models.CharField(
        max_length=20,
        unique=True,
        db_column='numero_factura',
        verbose_name='Número de Factura',
        help_text='Número único de factura'
    )
    empresa = models.CharField(
        max_length=20,
        choices=EmpresaFactura.choices,
        db_column='empresa',
        verbose_name='Empresa',
        help_text='Empresa principal de la factura. Si incluye productos de múltiples empresas, seleccione "Mixta"'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='facturas',
        db_column='cliente_id',
        verbose_name='Cliente'
    )
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='subtotal',
        verbose_name='Subtotal'
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='descuento',
        verbose_name='Descuento'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='total',
        verbose_name='Total'
    )
    total_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='total_pagado',
        verbose_name='Total Pagado'
    )
    saldo_pendiente = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='saldo_pendiente',
        verbose_name='Saldo Pendiente'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoFactura.choices,
        default=EstadoFactura.BORRADOR,
        db_column='estado',
        verbose_name='Estado'
    )
    
    # Información adicional
    observaciones = models.TextField(
        blank=True,
        null=True,
        db_column='observaciones',
        verbose_name='Observaciones'
    )
    
    # Auditoría
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='facturas_creadas',
        db_column='usuario_id',
        verbose_name='Usuario que creó la factura'
    )
    fecha_factura = models.DateTimeField(
        default=timezone.now,
        db_column='fecha_factura',
        verbose_name='Fecha de Factura'
    )
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        db_column='fecha_vencimiento',
        verbose_name='Fecha de Vencimiento',
        help_text='Fecha de vencimiento para pagos a crédito'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at'
    )
    
    class Meta:
        db_table = 'facturas'
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_factura', '-numero_factura']
        indexes = [
            models.Index(fields=['numero_factura']),
            models.Index(fields=['cliente', 'fecha_factura']),
            models.Index(fields=['estado', 'fecha_factura']),
            models.Index(fields=['empresa', 'fecha_factura']),
        ]
    
    def __str__(self):
        return f"Factura {self.numero_factura} - {self.cliente.nombre}"
    
    def calcular_totales(self):
        """Calcula los totales basándose en los detalles"""
        detalles = self.detalles.all()
        self.subtotal = sum(detalle.subtotal for detalle in detalles)
        self.total = self.subtotal - self.descuento
        self.saldo_pendiente = self.total - self.total_pagado
        
        # Actualizar estado según el saldo
        if self.total_pagado == 0:
            self.estado = EstadoFactura.PENDIENTE
        elif self.total_pagado < self.total:
            self.estado = EstadoFactura.PARCIAL
        elif self.total_pagado >= self.total:
            self.estado = EstadoFactura.PAGADA
        
        self.save(update_fields=['subtotal', 'total', 'saldo_pendiente', 'estado'])
    
    def puede_pagar_fiado(self, monto_fiado):
        """Verifica si el cliente puede pagar el monto a fiado"""
        if not self.cliente.permite_fiado:
            return False, "El cliente no tiene permitido el fiado"
        
        credito_disponible = self.cliente.credito_disponible
        if monto_fiado > credito_disponible:
            return False, f"Crédito insuficiente. Disponible: Q{credito_disponible:.2f}"
        
        return True, "Puede pagar a fiado"


class Cotizacion(models.Model):
    """
    Modelo para cotizaciones que pueden convertirse en facturas
    """
    numero_cotizacion = models.CharField(
        max_length=20,
        unique=True,
        db_column='numero_cotizacion',
        verbose_name='Número de Cotización',
        help_text='Número único de cotización'
    )
    empresa = models.CharField(
        max_length=20,
        choices=EmpresaFactura.choices,
        db_column='empresa',
        verbose_name='Empresa'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='cotizaciones',
        db_column='cliente_id',
        verbose_name='Cliente'
    )
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='subtotal',
        verbose_name='Subtotal'
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='descuento',
        verbose_name='Descuento'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='total',
        verbose_name='Total'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoCotizacion.choices,
        default=EstadoCotizacion.BORRADOR,
        db_column='estado',
        verbose_name='Estado'
    )
    
    # Información adicional
    observaciones = models.TextField(
        blank=True,
        null=True,
        db_column='observaciones',
        verbose_name='Observaciones'
    )
    condiciones = models.TextField(
        blank=True,
        null=True,
        db_column='condiciones',
        verbose_name='Condiciones de la Cotización',
        help_text='Términos y condiciones de la cotización'
    )
    
    # Fechas importantes
    fecha_vencimiento = models.DateField(
        db_column='fecha_vencimiento',
        verbose_name='Fecha de Vencimiento',
        help_text='Fecha hasta la cual la cotización es válida'
    )
    fecha_aceptacion = models.DateTimeField(
        blank=True,
        null=True,
        db_column='fecha_aceptacion',
        verbose_name='Fecha de Aceptación',
        help_text='Fecha en que el cliente aceptó la cotización'
    )
    
    # Relación con factura generada
    factura_generada = models.OneToOneField(
        Factura,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cotizacion_origen',
        db_column='factura_id',
        verbose_name='Factura Generada',
        help_text='Factura generada a partir de esta cotización'
    )
    
    # Auditoría
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='cotizaciones_creadas',
        db_column='usuario_id',
        verbose_name='Usuario que creó la cotización'
    )
    fecha_cotizacion = models.DateTimeField(
        default=timezone.now,
        db_column='fecha_cotizacion',
        verbose_name='Fecha de Cotización'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at'
    )
    
    class Meta:
        db_table = 'cotizaciones'
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
        ordering = ['-fecha_cotizacion', '-numero_cotizacion']
        indexes = [
            models.Index(fields=['numero_cotizacion']),
            models.Index(fields=['cliente', 'fecha_cotizacion']),
            models.Index(fields=['estado', 'fecha_cotizacion']),
            models.Index(fields=['empresa', 'fecha_cotizacion']),
            models.Index(fields=['fecha_vencimiento']),
        ]
    
    def __str__(self):
        return f"Cotización {self.numero_cotizacion} - {self.cliente.nombre}"
    
    def calcular_totales(self):
        """Calcula los totales basándose en los detalles"""
        detalles = self.detalles.all()
        self.subtotal = sum(detalle.subtotal for detalle in detalles)
        self.total = self.subtotal - self.descuento
        self.save(update_fields=['subtotal', 'total'])
    
    def esta_vencida(self):
        """Verifica si la cotización está vencida"""
        from django.utils import timezone
        if self.fecha_vencimiento and timezone.now().date() > self.fecha_vencimiento:
            return True
        return False
    
    def puede_convertir_factura(self):
        """Verifica si la cotización puede convertirse en factura"""
        if self.estado != EstadoCotizacion.ACEPTADA:
            return False, "La cotización debe estar aceptada para convertirla en factura"
        
        if self.factura_generada:
            return False, "Esta cotización ya tiene una factura generada"
        
        if self.esta_vencida():
            return False, "La cotización está vencida"
        
        # Verificar que todos los productos tengan stock suficiente
        for detalle in self.detalles.all():
            # Obtener el producto según el tipo
            if detalle.producto_empresa == EmpresaFactura.FERRETERIA:
                from ferreteria.models import Producto
                try:
                    producto = Producto.objects.get(codigo=detalle.producto_codigo, activo=True)
                    if producto.stock_actual < int(detalle.cantidad):
                        return False, f"Stock insuficiente para {detalle.producto_nombre}. Disponible: {producto.stock_actual}"
                except Producto.DoesNotExist:
                    return False, f"Producto {detalle.producto_nombre} no encontrado o inactivo"
            elif detalle.producto_empresa == EmpresaFactura.BLOQUERA:
                from bloquera.models import ProductoBloquera
                try:
                    producto = ProductoBloquera.objects.get(codigo=detalle.producto_codigo, activo=True)
                    if producto.stock_actual < int(detalle.cantidad):
                        return False, f"Stock insuficiente para {detalle.producto_nombre}. Disponible: {producto.stock_actual}"
                except ProductoBloquera.DoesNotExist:
                    return False, f"Producto {detalle.producto_nombre} no encontrado o inactivo"
            elif detalle.producto_empresa == EmpresaFactura.PIEDRINERA:
                from piedrinera.models import AgregadoPiedrinera
                try:
                    producto = AgregadoPiedrinera.objects.get(codigo=detalle.producto_codigo, activo=True)
                    if producto.stock_actual_m3 < detalle.cantidad:
                        return False, f"Stock insuficiente para {detalle.producto_nombre}. Disponible: {producto.stock_actual_m3} m³"
                except AgregadoPiedrinera.DoesNotExist:
                    return False, f"Producto {detalle.producto_nombre} no encontrado o inactivo"
        
        return True, "Puede convertirse en factura"


class DetalleCotizacion(models.Model):
    """
    Detalle de productos en una cotización (similar a DetalleFactura)
    """
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.CASCADE,
        related_name='detalles',
        db_column='cotizacion_id',
        verbose_name='Cotización'
    )
    
    # Generic Foreign Key para productos de cualquier empresa
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to={
            'model__in': ['producto', 'productobloquera', 'agregadopiedrinera']
        }
    )
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    # Información del producto al momento de la cotización
    producto_codigo = models.CharField(
        max_length=50,
        db_column='producto_codigo',
        verbose_name='Código del Producto'
    )
    producto_nombre = models.CharField(
        max_length=200,
        db_column='producto_nombre',
        verbose_name='Nombre del Producto'
    )
    producto_empresa = models.CharField(
        max_length=20,
        choices=EmpresaFactura.choices,
        db_column='producto_empresa',
        verbose_name='Empresa del Producto'
    )
    
    # Cantidad y precios
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        db_column='cantidad',
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='precio_unitario',
        verbose_name='Precio Unitario'
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='descuento',
        verbose_name='Descuento'
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='subtotal',
        verbose_name='Subtotal'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at'
    )
    
    class Meta:
        db_table = 'detalles_cotizacion'
        verbose_name = 'Detalle de Cotización'
        verbose_name_plural = 'Detalles de Cotización'
        ordering = ['cotizacion', 'id']
        indexes = [
            models.Index(fields=['cotizacion', 'producto_empresa']),
        ]
    
    def __str__(self):
        return f"{self.cotizacion.numero_cotizacion} - {self.producto_nombre} x{self.cantidad}"
    
    def calcular_subtotal(self):
        """Calcula el subtotal del detalle"""
        from decimal import Decimal
        cantidad = Decimal(str(self.cantidad))
        precio = Decimal(str(self.precio_unitario))
        descuento = Decimal(str(self.descuento))
        self.subtotal = (cantidad * precio) - descuento
        return self.subtotal
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal antes de guardar"""
        self.calcular_subtotal()
        super().save(*args, **kwargs)
        # Actualizar totales de la cotización
        self.cotizacion.calcular_totales()


class DetalleFactura(models.Model):
    """
    Detalle de productos en una factura (unificado para las tres empresas)
    Usa GenericForeignKey para referenciar productos de cualquier empresa
    """
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles',
        db_column='factura_id',
        verbose_name='Factura'
    )
    
    # Generic Foreign Key para productos de cualquier empresa
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to={
            'model__in': ['producto', 'productobloquera', 'agregadopiedrinera']
        }
    )
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    # Información del producto al momento de la venta (para historial)
    producto_codigo = models.CharField(
        max_length=50,
        db_column='producto_codigo',
        verbose_name='Código del Producto'
    )
    producto_nombre = models.CharField(
        max_length=200,
        db_column='producto_nombre',
        verbose_name='Nombre del Producto'
    )
    producto_empresa = models.CharField(
        max_length=20,
        choices=EmpresaFactura.choices,
        db_column='producto_empresa',
        verbose_name='Empresa del Producto'
    )
    
    # Cantidad y precios
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        db_column='cantidad',
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='precio_unitario',
        verbose_name='Precio Unitario'
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='descuento',
        verbose_name='Descuento'
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='subtotal',
        verbose_name='Subtotal'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at'
    )
    
    class Meta:
        db_table = 'detalles_factura'
        verbose_name = 'Detalle de Factura'
        verbose_name_plural = 'Detalles de Factura'
        ordering = ['factura', 'id']
        indexes = [
            models.Index(fields=['factura', 'producto_empresa']),
        ]
    
    def __str__(self):
        return f"{self.factura.numero_factura} - {self.producto_nombre} x{self.cantidad}"
    
    def calcular_subtotal(self):
        """Calcula el subtotal del detalle"""
        from decimal import Decimal
        cantidad = Decimal(str(self.cantidad))
        precio = Decimal(str(self.precio_unitario))
        descuento = Decimal(str(self.descuento))
        self.subtotal = (cantidad * precio) - descuento
        return self.subtotal
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal antes de guardar"""
        self.calcular_subtotal()
        super().save(*args, **kwargs)
        # Actualizar totales de la factura
        self.factura.calcular_totales()


class Pago(models.Model):
    """
    Modelo para pagos de facturas (permite múltiples formas de pago)
    """
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='pagos',
        db_column='factura_id',
        verbose_name='Factura'
    )
    tipo_pago = models.CharField(
        max_length=20,
        choices=TipoPago.choices,
        db_column='tipo_pago',
        verbose_name='Tipo de Pago'
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        db_column='monto',
        verbose_name='Monto'
    )
    
    # Información adicional según el tipo de pago
    referencia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column='referencia',
        verbose_name='Referencia',
        help_text='Número de tarjeta, referencia de transferencia, etc.'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        db_column='observaciones',
        verbose_name='Observaciones'
    )
    
    # Auditoría
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='pagos_registrados',
        db_column='usuario_id',
        verbose_name='Usuario que registró el pago'
    )
    fecha_pago = models.DateTimeField(
        default=timezone.now,
        db_column='fecha_pago',
        verbose_name='Fecha de Pago'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at'
    )
    
    class Meta:
        db_table = 'pagos'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']
        indexes = [
            models.Index(fields=['factura', 'fecha_pago']),
            models.Index(fields=['tipo_pago', 'fecha_pago']),
        ]
    
    def __str__(self):
        return f"Pago {self.get_tipo_pago_display()} - Q{self.monto:.2f} - Factura {self.factura.numero_factura}"
    
    def save(self, *args, **kwargs):
        """Actualiza el total pagado de la factura y el saldo del cliente si es fiado"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Actualizar total pagado de la factura
            self.factura.total_pagado = sum(pago.monto for pago in self.factura.pagos.all())
            self.factura.calcular_totales()
            
            # Si es pago a fiado, actualizar saldo del cliente
            if self.tipo_pago == TipoPago.FIADO:
                self.factura.cliente.saldo_actual += self.monto
                self.factura.cliente.save(update_fields=['saldo_actual', 'updated_at'])
