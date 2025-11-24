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
