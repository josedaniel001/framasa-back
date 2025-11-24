from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from authentication.models import Usuario


class AgregadoPiedrinera(models.Model):
    """
    Modelo para agregados de piedrinera (arena, grava, piedrín)
    """
    codigo = models.CharField(max_length=20, unique=True, db_column='codigo')
    nombre = models.CharField(max_length=150, db_column='nombre')
    descripcion = models.TextField(blank=True, null=True, db_column='descripcion')
    
    tipo = models.CharField(max_length=50, db_column='tipo')
    granulometria = models.CharField(max_length=50, blank=True, null=True, db_column='granulometria')
    
    precio_venta_m3 = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        db_column='precio_venta_m3'
    )
    costo_produccion_m3 = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        db_column='costo_produccion_m3'
    )
    
    stock_actual_m3 = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        db_column='stock_actual_m3'
    )
    stock_minimo_m3 = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        db_column='stock_minimo_m3'
    )
    
    ubicacion = models.CharField(max_length=100, blank=True, null=True, db_column='ubicacion')
    humedad_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        db_column='humedad_porcentaje'
    )
    calidad = models.CharField(max_length=30, blank=True, null=True, db_column='calidad')
    proveedor = models.CharField(max_length=150, blank=True, null=True, db_column='proveedor')
    fecha_ultima_entrada = models.DateField(blank=True, null=True, db_column='fecha_ultima_entrada')
    
    activo = models.BooleanField(default=True, db_column='activo')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'agregados_piedrinera'
        verbose_name = 'Agregado Piedrinera'
        verbose_name_plural = 'Agregados Piedrinera'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['nombre'], name='idx_agregados_nombre'),
            models.Index(fields=['tipo'], name='idx_agregados_tipo'),
            models.Index(fields=['proveedor'], name='idx_agregados_proveedor'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(stock_actual_m3__gte=0),
                name='chk_agregados_stock_actual_nonneg'
            ),
            models.CheckConstraint(
                check=models.Q(stock_minimo_m3__gte=0),
                name='chk_agregados_stock_minimo_nonneg'
            ),
            models.CheckConstraint(
                check=models.Q(precio_venta_m3__gte=0, costo_produccion_m3__gte=0),
                name='chk_agregados_precio_nonneg'
            ),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def tiene_stock_bajo(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock_actual_m3 <= self.stock_minimo_m3


class Camion(models.Model):
    """
    Modelo para camiones de la piedrinera
    """
    placa = models.CharField(max_length=15, unique=True, db_column='placa')
    marca = models.CharField(max_length=100, db_column='marca')
    modelo = models.CharField(max_length=100, db_column='modelo')
    
    capacidad_m3 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='capacidad_m3'
    )
    
    estado_actual = models.CharField(max_length=20, db_column='estado_actual')
    
    fecha_ultimo_mantenimiento = models.DateField(blank=True, null=True, db_column='fecha_ultimo_mantenimiento')
    fecha_proximo_mantenimiento = models.DateField(blank=True, null=True, db_column='fecha_proximo_mantenimiento')
    
    kilometraje = models.IntegerField(default=0, validators=[MinValueValidator(0)], db_column='kilometraje')
    horas_operacion = models.IntegerField(default=0, validators=[MinValueValidator(0)], db_column='horas_operacion')
    consumo_l_100km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='consumo_l_100km'
    )
    
    seguro_vigente = models.BooleanField(default=True, db_column='seguro_vigente')
    revision_tecnica_vigente = models.BooleanField(default=True, db_column='revision_tecnica_vigente')
    documentacion_vigente = models.BooleanField(default=True, db_column='documentacion_vigente')
    
    observaciones = models.TextField(blank=True, null=True, db_column='observaciones')
    
    activo = models.BooleanField(default=True, db_column='activo')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'camiones'
        verbose_name = 'Camión'
        verbose_name_plural = 'Camiones'
        ordering = ['placa']
        indexes = [
            models.Index(fields=['placa'], name='idx_camiones_placa'),
            models.Index(fields=['marca', 'modelo'], name='idx_camiones_marca_modelo'),
            models.Index(fields=['estado_actual'], name='idx_camiones_estado'),
            models.Index(fields=['fecha_proximo_mantenimiento'], name='idx_camiones_prox_mant'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(capacidad_m3__gte=0),
                name='chk_camiones_capacidad_nonneg'
            ),
            models.CheckConstraint(
                check=models.Q(kilometraje__gte=0),
                name='chk_camiones_km_nonneg'
            ),
            models.CheckConstraint(
                check=models.Q(horas_operacion__gte=0),
                name='chk_camiones_horas_nonneg'
            ),
            models.CheckConstraint(
                check=models.Q(consumo_l_100km__gte=0),
                name='chk_camiones_consumo_nonneg'
            ),
        ]

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"


class TipoMovimientoPiedrinera(models.TextChoices):
    """
    Tipos de movimientos de inventario para piedrinera
    """
    ENTRADA = 'ENTRADA', 'Entrada'
    SALIDA = 'SALIDA', 'Salida'
    AJUSTE = 'AJUSTE', 'Ajuste'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'
    DEVOLUCION = 'DEVOLUCION', 'Devolución'


class MovimientoInventarioPiedrinera(models.Model):
    """
    Modelo para movimientos de inventario de agregados de piedrinera
    Usa DecimalField para manejar cantidades en m³ con decimales
    """
    producto = models.ForeignKey(
        AgregadoPiedrinera,
        on_delete=models.PROTECT,
        related_name='movimientos',
        db_column='producto_id'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimientoPiedrinera.choices,
        db_column='tipo'
    )
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column='cantidad',
        help_text='Cantidad del movimiento en m³ (positiva para entrada/salida, puede ser negativa para ajustes)'
    )
    stock_anterior = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column='stock_anterior',
        help_text='Stock antes del movimiento'
    )
    stock_nuevo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
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
        related_name='movimientos_inventario_piedrinera',
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
        db_table = 'movimientos_inventario_piedrinera'
        verbose_name = 'Movimiento de Inventario Piedrinera'
        verbose_name_plural = 'Movimientos de Inventario Piedrinera'
        ordering = ['-fecha_movimiento']
        indexes = [
            models.Index(fields=['producto', 'fecha_movimiento']),
            models.Index(fields=['tipo', 'fecha_movimiento']),
            models.Index(fields=['fecha_movimiento']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.codigo} - {self.cantidad} m³"

    def clean(self):
        """
        Validación personalizada
        """
        from django.core.exceptions import ValidationError
        from decimal import Decimal
        
        # Para ENTRADA, SALIDA, DEVOLUCION, TRANSFERENCIA: cantidad debe ser positiva
        if self.tipo in [TipoMovimientoPiedrinera.ENTRADA, TipoMovimientoPiedrinera.SALIDA, 
                         TipoMovimientoPiedrinera.DEVOLUCION, TipoMovimientoPiedrinera.TRANSFERENCIA]:
            if self.cantidad <= Decimal('0'):
                raise ValidationError({
                    'cantidad': 'La cantidad debe ser mayor a 0 para este tipo de movimiento'
                })
        
        # Para SALIDA y TRANSFERENCIA: verificar que haya stock suficiente
        if self.tipo in [TipoMovimientoPiedrinera.SALIDA, TipoMovimientoPiedrinera.TRANSFERENCIA]:
            if hasattr(self, 'producto') and self.producto:
                if self.producto.stock_actual_m3 < self.cantidad:
                    raise ValidationError({
                        'cantidad': f'Stock insuficiente. Stock actual: {self.producto.stock_actual_m3} m³'
                    })

    def save(self, *args, **kwargs):
        """
        Actualiza el stock del producto al guardar el movimiento
        """
        if not self.pk:  # Solo en creación
            self.clean()  # Validar antes de guardar
            from decimal import Decimal
            self.stock_anterior = self.producto.stock_actual_m3
            
            # Calcular nuevo stock según el tipo de movimiento
            if self.tipo == TipoMovimientoPiedrinera.ENTRADA:
                self.stock_nuevo = self.stock_anterior + self.cantidad
            elif self.tipo == TipoMovimientoPiedrinera.SALIDA:
                self.stock_nuevo = max(Decimal('0'), self.stock_anterior - self.cantidad)
            elif self.tipo == TipoMovimientoPiedrinera.AJUSTE:
                # Para ajustes, la cantidad puede ser positiva (incremento) o negativa (decremento)
                self.stock_nuevo = max(Decimal('0'), self.stock_anterior + self.cantidad)
            elif self.tipo == TipoMovimientoPiedrinera.DEVOLUCION:
                self.stock_nuevo = self.stock_anterior + self.cantidad
            else:  # TRANSFERENCIA
                self.stock_nuevo = max(Decimal('0'), self.stock_anterior - self.cantidad)
            
            # Actualizar el stock del producto
            self.producto.stock_actual_m3 = self.stock_nuevo
            self.producto.save(update_fields=['stock_actual_m3', 'updated_at'])
        
        super().save(*args, **kwargs)