from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


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