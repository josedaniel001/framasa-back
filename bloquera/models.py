from django.db import models
from django.utils import timezone


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
