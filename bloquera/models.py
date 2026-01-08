from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from authentication.models import Usuario


class ProductoBloquera(models.Model):
    """
    Modelo para productos de bloquera
    """
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    
    # Texto libre en vez de FK
    tipo_bloque = models.CharField(max_length=100)
    dimensiones = models.CharField(max_length=50, blank=True, null=True)
    
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_descuento = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        db_column='precio_descuento',
        help_text='Precio con descuento aplicado (opcional)'
    )
    costo_produccion = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    
    activo = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'productos_bloquera'
        verbose_name = 'Producto Bloquera'
        verbose_name_plural = 'Productos Bloquera'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
            models.Index(fields=['tipo_bloque']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def tiene_stock_bajo(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock_actual <= self.stock_minimo


class TipoMovimientoBloquera(models.TextChoices):
    """
    Tipos de movimientos de inventario para bloquera
    """
    ENTRADA = 'ENTRADA', 'Entrada'
    SALIDA = 'SALIDA', 'Salida'
    AJUSTE = 'AJUSTE', 'Ajuste'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'
    DEVOLUCION = 'DEVOLUCION', 'Devolución'


class MovimientoInventarioBloquera(models.Model):
    """
    Modelo para movimientos de inventario de productos de bloquera
    """
    producto = models.ForeignKey(
        ProductoBloquera,
        on_delete=models.PROTECT,
        related_name='movimientos',
        db_column='producto_id'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimientoBloquera.choices,
        db_column='tipo'
    )
    cantidad = models.IntegerField(
        db_column='cantidad',
        help_text='Cantidad del movimiento (positiva para entrada/salida, puede ser negativa para ajustes)'
    )
    stock_anterior = models.IntegerField(
        default=0,
        db_column='stock_anterior',
        help_text='Stock antes del movimiento'
    )
    stock_nuevo = models.IntegerField(
        default=0,
        db_column='stock_nuevo',
        help_text='Stock después del movimiento'
    )
    motivo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        db_column='motivo',
        help_text='Motivo del movimiento'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        db_column='observaciones'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='movimientos_inventario_bloquera',
        db_column='usuario_id',
        help_text='Usuario que realizó el movimiento'
    )
    fecha_movimiento = models.DateTimeField(
        auto_now_add=True,
        db_column='fecha_movimiento'
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
        db_table = 'movimientos_inventario_bloquera'
        verbose_name = 'Movimiento de Inventario Bloquera'
        verbose_name_plural = 'Movimientos de Inventario Bloquera'
        ordering = ['-fecha_movimiento']
        indexes = [
            models.Index(fields=['producto', 'fecha_movimiento']),
            models.Index(fields=['tipo', 'fecha_movimiento']),
            models.Index(fields=['fecha_movimiento']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.codigo} - {self.cantidad}"

    def clean(self):
        """
        Validación personalizada
        """
        from django.core.exceptions import ValidationError
        
        # Para ENTRADA, SALIDA, DEVOLUCION, TRANSFERENCIA: cantidad debe ser positiva
        if self.tipo in [TipoMovimientoBloquera.ENTRADA, TipoMovimientoBloquera.SALIDA, 
                         TipoMovimientoBloquera.DEVOLUCION, TipoMovimientoBloquera.TRANSFERENCIA]:
            if self.cantidad <= 0:
                raise ValidationError({
                    'cantidad': 'La cantidad debe ser mayor a 0 para este tipo de movimiento'
                })
        
        # Para SALIDA y TRANSFERENCIA: verificar que haya stock suficiente
        if self.tipo in [TipoMovimientoBloquera.SALIDA, TipoMovimientoBloquera.TRANSFERENCIA]:
            if hasattr(self, 'producto') and self.producto:
                if self.producto.stock_actual < self.cantidad:
                    raise ValidationError({
                        'cantidad': f'Stock insuficiente. Stock actual: {self.producto.stock_actual}'
                    })

    def save(self, *args, **kwargs):
        """
        Actualiza el stock del producto al guardar el movimiento
        """
        if not self.pk:  # Solo en creación
            self.clean()  # Validar antes de guardar
            self.stock_anterior = self.producto.stock_actual
            
            # Calcular nuevo stock según el tipo de movimiento
            if self.tipo == TipoMovimientoBloquera.ENTRADA:
                self.stock_nuevo = self.stock_anterior + self.cantidad
            elif self.tipo == TipoMovimientoBloquera.SALIDA:
                self.stock_nuevo = max(0, self.stock_anterior - self.cantidad)
            elif self.tipo == TipoMovimientoBloquera.AJUSTE:
                # Para ajustes, la cantidad puede ser positiva (incremento) o negativa (decremento)
                self.stock_nuevo = max(0, self.stock_anterior + self.cantidad)
            elif self.tipo == TipoMovimientoBloquera.DEVOLUCION:
                self.stock_nuevo = self.stock_anterior + self.cantidad
            else:  # TRANSFERENCIA
                self.stock_nuevo = max(0, self.stock_anterior - self.cantidad)
            
            # Actualizar el stock del producto
            self.producto.stock_actual = self.stock_nuevo
            self.producto.save(update_fields=['stock_actual', 'updated_at'])
        
        super().save(*args, **kwargs)


class EstadoOrdenProduccionBloquera(models.TextChoices):
    """
    Estados posibles para órdenes de producción de bloquera
    """
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    EN_PROCESO = 'EN_PROCESO', 'En Proceso'
    COMPLETADA = 'COMPLETADA', 'Completada'
    CANCELADA = 'CANCELADA', 'Cancelada'


class OrdenProduccionBloquera(models.Model):
    """
    Modelo para órdenes de producción de bloquera
    """
    codigo = models.CharField(
        max_length=20,
        unique=True,
        db_column='codigo',
        help_text='Código único de la orden (ej: OP-2025-0001)'
    )
    producto = models.ForeignKey(
        ProductoBloquera,
        on_delete=models.RESTRICT,
        related_name='ordenes_produccion',
        db_column='producto_id',
        help_text='Producto a producir'
    )

    cantidad_solicitada = models.IntegerField(
        db_column='cantidad_solicitada',
        help_text='Cantidad total solicitada para la orden',
        validators=[MinValueValidator(0)]
    )
    fecha_inicio = models.DateField(
        db_column='fecha_inicio',
        help_text='Fecha de inicio de la orden de producción'
    )
    fecha_fin_estimada = models.DateField(
        blank=True,
        null=True,
        db_column='fecha_fin_estimada',
        help_text='Fecha estimada de finalización'
    )

    supervisor = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        db_column='supervisor',
        help_text='Responsable/supervisor de la orden'
    )
    notas = models.TextField(
        blank=True,
        null=True,
        db_column='notas',
        help_text='Notas adicionales sobre la orden'
    )

    estado = models.CharField(
        max_length=20,
        choices=EstadoOrdenProduccionBloquera.choices,
        default=EstadoOrdenProduccionBloquera.PENDIENTE,
        db_column='estado',
        help_text='Estado actual de la orden de producción'
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
        db_table = 'ordenes_produccion_bloquera'
        verbose_name = 'Orden de Producción Bloquera'
        verbose_name_plural = 'Órdenes de Producción Bloquera'
        ordering = ['-fecha_inicio', '-created_at']
        indexes = [
            models.Index(fields=['codigo'], name='idx_op_codigo'),
            models.Index(fields=['estado'], name='idx_op_estado'),
            models.Index(fields=['producto'], name='idx_op_producto'),
            models.Index(fields=['fecha_inicio'], name='idx_op_fecha_inicio'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(cantidad_solicitada__gte=0),
                name='chk_op_cant_solicitada'
            ),
            models.CheckConstraint(
                check=models.Q(fecha_fin_estimada__isnull=True) |
                      models.Q(fecha_fin_estimada__gte=models.F('fecha_inicio')),
                name='chk_op_fechas'
            ),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.producto.nombre}"

    @property
    def cantidad_producida_total(self):
        """Calcula la cantidad total producida en todos los lotes de esta orden"""
        from django.db.models import Sum
        result = self.lotes_produccion.aggregate(
            total=Sum('cantidad_producida')
        )
        return result['total'] or 0

    @property
    def cantidad_pendiente(self):
        """Calcula la cantidad que aún falta por producir"""
        return max(0, self.cantidad_solicitada - self.cantidad_producida_total)

    @property
    def progreso_porcentaje(self):
        """Calcula el porcentaje de progreso de la orden"""
        if self.cantidad_solicitada == 0:
            return 100.0
        return min(100.0, (self.cantidad_producida_total / self.cantidad_solicitada) * 100)

    @property
    def esta_completada(self):
        """Verifica si la orden está completamente producida"""
        return self.cantidad_producida_total >= self.cantidad_solicitada

    @property
    def esta_vencida(self):
        """Verifica si la orden está vencida (fecha estimada pasada y no completada)"""
        if not self.fecha_fin_estimada or self.estado == EstadoOrdenProduccionBloquera.COMPLETADA:
            return False
        from django.utils import timezone
        return timezone.now().date() > self.fecha_fin_estimada


class CalidadLoteBloquera(models.TextChoices):
    """
    Niveles de calidad para lotes de producción
    """
    MALA = 'MALA', 'Mala'
    REGULAR = 'REGULAR', 'Regular'
    BUENA = 'BUENA', 'Buena'
    EXCELENTE = 'EXCELENTE', 'Excelente'


class LoteProduccionBloquera(models.Model):
    """
    Modelo para lotes de producción de bloquera
    Cada lote representa una sesión de producción dentro de una orden
    """
    orden = models.ForeignKey(
        OrdenProduccionBloquera,
        on_delete=models.CASCADE,
        related_name='lotes_produccion',
        db_column='orden_id',
        help_text='Orden de producción a la que pertenece este lote'
    )

    fecha_lote = models.DateField(
        db_column='fecha_lote',
        help_text='Fecha en que se produjo este lote'
    )
    hora_inicio = models.TimeField(
        db_column='hora_inicio',
        help_text='Hora de inicio de la producción del lote'
    )
    hora_fin = models.TimeField(
        db_column='hora_fin',
        help_text='Hora de finalización de la producción del lote'
    )

    cantidad_producida = models.IntegerField(
        db_column='cantidad_producida',
        help_text='Cantidad total producida en este lote',
        validators=[MinValueValidator(0)]
    )
    cantidad_defectuosa = models.IntegerField(
        db_column='cantidad_defectuosa',
        default=0,
        help_text='Cantidad de productos defectuosos en este lote',
        validators=[MinValueValidator(0)]
    )

    calidad = models.CharField(
        max_length=20,
        choices=CalidadLoteBloquera.choices,
        db_column='calidad',
        help_text='Calidad del lote producido'
    )

    supervisor = models.CharField(
        max_length=120,
        db_column='supervisor',
        help_text='Supervisor que registró este lote (snapshot de la orden)'
    )
    notas = models.TextField(
        blank=True,
        null=True,
        db_column='notas',
        help_text='Notas adicionales sobre este lote'
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
        db_table = 'lotes_produccion_bloquera'
        verbose_name = 'Lote de Producción Bloquera'
        verbose_name_plural = 'Lotes de Producción Bloquera'
        ordering = ['-fecha_lote', '-hora_inicio']
        indexes = [
            models.Index(fields=['orden'], name='idx_lotes_orden'),
            models.Index(fields=['fecha_lote'], name='idx_lotes_fecha'),
            models.Index(fields=['calidad'], name='idx_lotes_calidad'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(hora_fin__gt=models.F('hora_inicio')),
                name='chk_lote_horas'
            ),
            models.CheckConstraint(
                check=models.Q(
                    models.Q(cantidad_producida__gte=0) &
                    models.Q(cantidad_defectuosa__gte=0) &
                    models.Q(cantidad_defectuosa__lte=models.F('cantidad_producida'))
                ),
                name='chk_lote_cantidades'
            ),
        ]

    def __str__(self):
        return f"Lote {self.orden.codigo} - {self.fecha_lote}"

    def clean(self):
        """
        Validación personalizada adicional
        """
        from django.core.exceptions import ValidationError

        # Validar que la fecha del lote esté dentro del período de la orden
        if hasattr(self, 'orden') and self.orden:
            if self.fecha_lote < self.orden.fecha_inicio:
                raise ValidationError({
                    'fecha_lote': 'La fecha del lote no puede ser anterior a la fecha de inicio de la orden'
                })

            if self.orden.fecha_fin_estimada and self.fecha_lote > self.orden.fecha_fin_estimada:
                raise ValidationError({
                    'fecha_lote': 'La fecha del lote no puede ser posterior a la fecha estimada de fin de la orden'
                })

    def save(self, *args, **kwargs):
        """
        Actualizar stock del producto al guardar el lote
        """
        if not self.pk:  # Solo en creación
            self.clean()  # Validar antes de guardar

            # Actualizar stock del producto (solo cantidad buena)
            cantidad_buena = self.cantidad_producida - self.cantidad_defectuosa
            if cantidad_buena > 0:
                # Crear movimiento de inventario para entrada de producción
                # Obtener el usuario del contexto si está disponible
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    # Intentar obtener el usuario del contexto (si está disponible)
                    usuario = getattr(self, '_usuario_context', None)
                    if not usuario:
                        # Si no hay contexto, usar el primer usuario activo como fallback
                        usuario = User.objects.filter(is_active=True).first()
                    if usuario:
                        MovimientoInventarioBloquera.objects.create(
                            producto=self.orden.producto,
                            tipo='ENTRADA',
                            cantidad=cantidad_buena,
                            motivo=f'Producción lote {self.fecha_lote}',
                            observaciones=f'Lote de orden {self.orden.codigo} - Calidad: {self.get_calidad_display()}',
                            usuario=usuario
                        )
                except Exception as e:
                    # Si hay error al crear el movimiento, loguear pero no fallar el guardado del lote
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f'No se pudo crear movimiento de inventario para lote {self.id}: {str(e)}')

        super().save(*args, **kwargs)

    @property
    def cantidad_buena(self):
        """Calcula la cantidad de productos buenos (total - defectuosos)"""
        return max(0, self.cantidad_producida - self.cantidad_defectuosa)

    @property
    def porcentaje_defectuoso(self):
        """Calcula el porcentaje de productos defectuosos"""
        if self.cantidad_producida == 0:
            return 0.0
        return (self.cantidad_defectuosa / self.cantidad_producida) * 100

    @property
    def duracion_horas(self):
        """Calcula la duración del lote en horas"""
        from datetime import datetime, date
        inicio = datetime.combine(date.today(), self.hora_inicio)
        fin = datetime.combine(date.today(), self.hora_fin)
        duracion = fin - inicio
        return duracion.total_seconds() / 3600

    @property
    def rendimiento_por_hora(self):
        """Calcula el rendimiento en unidades por hora"""
        if self.duracion_horas == 0:
            return 0.0
        return self.cantidad_producida / self.duracion_horas
