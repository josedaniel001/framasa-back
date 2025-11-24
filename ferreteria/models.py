from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from authentication.models import Usuario


class CategoriaProducto(models.Model):
    """
    Modelo para categorías de productos
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'categorias_producto'
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    """
    Modelo para unidades de medida
    """
    nombre = models.CharField(max_length=50, unique=True)
    abreviatura = models.CharField(max_length=10, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'unidades_medida'
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"


class Producto(models.Model):
    """
    Modelo para productos de ferretería
    """
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        related_name='productos',
        db_column='categoria_id'
    )
    unidad_medida = models.ForeignKey(
        UnidadMedida,
        on_delete=models.PROTECT,
        related_name='productos',
        db_column='unidad_medida_id'
    )
    proveedor = models.ForeignKey(
        'Proveedor',
        on_delete=models.SET_NULL,
        related_name='productos',
        db_column='proveedor_id',
        blank=True,
        null=True
    )

    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)

    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def tiene_stock_bajo(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock_actual <= self.stock_minimo


class Cliente(models.Model):
    """
    Modelo para clientes de ferretería
    """
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=25, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Campos de fiado (crédito)
    permite_fiado = models.BooleanField(
        default=False,
        help_text='Indica si el cliente puede comprar a crédito'
    )
    limite_credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Límite máximo de crédito permitido para el cliente'
    )
    saldo_actual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Saldo actual de crédito utilizado por el cliente'
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True, db_column='fecha_registro')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['nit']),
            models.Index(fields=['activo']),
            models.Index(fields=['permite_fiado']),
        ]

    def __str__(self):
        return self.nombre
    
    @property
    def credito_disponible(self):
        """Calcula el crédito disponible (límite - saldo actual)"""
        if not self.permite_fiado:
            return 0
        disponible = self.limite_credito - self.saldo_actual
        return max(0, disponible)
    
    @property
    def puede_comprar_fiado(self):
        """Verifica si el cliente puede realizar una compra a crédito"""
        if not self.permite_fiado or not self.activo:
            return False
        return self.saldo_actual < self.limite_credito


class Proveedor(models.Model):
    """
    Modelo para proveedores de productos
    """
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=25, blank=True, null=True, unique=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    contacto = models.CharField(max_length=150, blank=True, null=True, help_text='Nombre del contacto principal')
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, db_column='fecha_registro')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'proveedores'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['nit']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return self.nombre


class TipoMovimiento(models.TextChoices):
    """
    Tipos de movimientos de inventario
    """
    ENTRADA = 'ENTRADA', 'Entrada'
    SALIDA = 'SALIDA', 'Salida'
    AJUSTE = 'AJUSTE', 'Ajuste'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'
    DEVOLUCION = 'DEVOLUCION', 'Devolución'


class MovimientoInventario(models.Model):
    """
    Modelo para movimientos de inventario de productos de ferretería
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos',
        db_column='producto_id'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimiento.choices,
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
        related_name='movimientos_inventario_ferreteria',
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
        db_table = 'movimientos_inventario'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
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
        if self.tipo in [TipoMovimiento.ENTRADA, TipoMovimiento.SALIDA, 
                         TipoMovimiento.DEVOLUCION, TipoMovimiento.TRANSFERENCIA]:
            if self.cantidad <= 0:
                raise ValidationError({
                    'cantidad': 'La cantidad debe ser mayor a 0 para este tipo de movimiento'
                })
        
        # Para SALIDA y TRANSFERENCIA: verificar que haya stock suficiente
        if self.tipo in [TipoMovimiento.SALIDA, TipoMovimiento.TRANSFERENCIA]:
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
            if self.tipo == TipoMovimiento.ENTRADA:
                self.stock_nuevo = self.stock_anterior + self.cantidad
            elif self.tipo == TipoMovimiento.SALIDA:
                self.stock_nuevo = max(0, self.stock_anterior - self.cantidad)
            elif self.tipo == TipoMovimiento.AJUSTE:
                # Para ajustes, la cantidad puede ser positiva (incremento) o negativa (decremento)
                self.stock_nuevo = max(0, self.stock_anterior + self.cantidad)
            elif self.tipo == TipoMovimiento.DEVOLUCION:
                self.stock_nuevo = self.stock_anterior + self.cantidad
            else:  # TRANSFERENCIA
                self.stock_nuevo = max(0, self.stock_anterior - self.cantidad)
            
            # Actualizar el stock del producto
            self.producto.stock_actual = self.stock_nuevo
            self.producto.save(update_fields=['stock_actual', 'updated_at'])
        
        super().save(*args, **kwargs)