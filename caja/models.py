from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from ferreteria.models import UnidadMedida


class EmpresaCaja(models.TextChoices):
    """Empresas para movimientos de caja"""
    FERRETERIA = 'Ferretería', 'Ferretería'
    BLOQUERA = 'Bloquera', 'Bloquera'
    PIEDRINERA = 'Piedrinera', 'Piedrinera'
    TALLER = 'Taller', 'Taller'


class TipoMovimientoCaja(models.TextChoices):
    """Tipos de movimiento de caja"""
    ENTRADA = 'ENTRADA', 'Entrada'
    SALIDA = 'SALIDA', 'Salida'


class EstadoMovimientoCaja(models.TextChoices):
    """Estados de un movimiento de caja"""
    BORRADOR = 'BORRADOR', 'Borrador'
    CONFIRMADO = 'CONFIRMADO', 'Confirmado'
    ANULADO = 'ANULADO', 'Anulado'


class MovimientoCaja(models.Model):
    """
    Modelo para movimientos de caja
    """
    empresa = models.CharField(
        max_length=30,
        choices=EmpresaCaja.choices,
        db_column='empresa',
        verbose_name='Empresa'
    )
    
    tipo = models.CharField(
        max_length=10,
        choices=TipoMovimientoCaja.choices,
        db_column='tipo',
        verbose_name='Tipo'
    )
    
    fecha_hora = models.DateTimeField(
        default=timezone.now,
        db_column='fecha_hora',
        verbose_name='Fecha y Hora'
    )
    
    referencia = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='referencia',
        verbose_name='Referencia',
        help_text='FAC-001 / REC-001 / COMP-001 etc'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        db_column='descripcion',
        verbose_name='Descripción'
    )
    
    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='total',
        verbose_name='Total'
    )
    
    estado = models.CharField(
        max_length=12,
        choices=EstadoMovimientoCaja.choices,
        default=EstadoMovimientoCaja.CONFIRMADO,
        db_column='estado',
        verbose_name='Estado'
    )
    
    # Auditoría (created_by_id es BIGINT NULL, no FK)
    created_by_id = models.BigIntegerField(
        blank=True,
        null=True,
        db_column='created_by_id',
        verbose_name='ID del Usuario que Creó'
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
        db_table = 'caja_movimiento'
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['-fecha_hora'], name='idx_caja_movimiento_fecha'),
            models.Index(fields=['tipo'], name='idx_caja_movimiento_tipo'),
            models.Index(fields=['empresa'], name='idx_caja_movimiento_empresa'),
            models.Index(fields=['referencia'], name='idx_caja_movimiento_referencia'),
        ]
    
    def __str__(self):
        referencia_str = f" - {self.referencia}" if self.referencia else ""
        return f"{self.get_tipo_display()} - {self.get_empresa_display()}{referencia_str} - Q{self.total:.2f}"


class MovimientoCajaDetalle(models.Model):
    """
    Modelo para detalles de movimientos de caja
    """
    movimiento = models.ForeignKey(
        MovimientoCaja,
        on_delete=models.CASCADE,
        related_name='detalles',
        db_column='movimiento_id',
        verbose_name='Movimiento'
    )
    
    producto_nombre = models.CharField(
        max_length=150,
        db_column='producto_nombre',
        verbose_name='Nombre del Producto'
    )
    
    cantidad = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='cantidad',
        verbose_name='Cantidad'
    )
    
    unidad_medida = models.ForeignKey(
        UnidadMedida,
        on_delete=models.PROTECT,
        related_name='movimientos_caja_detalle',
        db_column='unidad_medida_id',
        verbose_name='Unidad de Medida',
        null=True,
        blank=True
    )
    
    costo_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='costo_total',
        verbose_name='Costo Total'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    
    class Meta:
        db_table = 'caja_movimiento_detalle'
        verbose_name = 'Detalle de Movimiento de Caja'
        verbose_name_plural = 'Detalles de Movimiento de Caja'
        ordering = ['movimiento', 'id']
        indexes = [
            models.Index(fields=['movimiento'], name='idx_caja_detalle_movimiento'),
        ]
    
    def __str__(self):
        return f"{self.movimiento} - {self.producto_nombre} x{self.cantidad}"
