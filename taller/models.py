# Modelos del módulo Taller

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class EmpresaMaquinaria(models.TextChoices):
    """
    Empresas que pueden tener maquinaria
    """
    FERRETERIA = 'FERRETERIA', 'Ferretería'
    BLOQUERA = 'BLOQUERA', 'Bloquera'
    PIEDRINERA = 'PIEDRINERA', 'Piedrinera'
    CONSTRUCTORA = 'CONSTRUCTORA', 'Constructora'


class TipoMaquinaria(models.TextChoices):
    """
    Tipos de maquinaria disponibles (excluyendo camiones que se manejan en PIEDRINERA)
    """
    EXCAVADORA = 'EXCAVADORA', 'Excavadora'
    RETROEXCAVADORA = 'RETROEXCAVADORA', 'Retroexcavadora'
    CARGADOR = 'CARGADOR', 'Cargador Frontal'
    COMPACTADORA = 'COMPACTADORA', 'Compactadora'
    VIBRADOR = 'VIBRADOR', 'Vibrador de Concreto'
    MEZCLADORA = 'MEZCLADORA', 'Mezcladora de Concreto'
    CORTADORA = 'CORTADORA', 'Cortadora de Concreto'
    GENERADOR = 'GENERADOR', 'Generador'
    COMPRESOR = 'COMPRESOR', 'Compresor de Aire'
    SOLDADORA = 'SOLDADORA', 'Soldadora'
    OTRO = 'OTRO', 'Otro'


class Maquinaria(models.Model):
    """
    Modelo para maquinaria de las diferentes empresas
    Excluye camiones que se manejan en el módulo PIEDRINERA
    """
    # Identificación
    codigo = models.CharField(
        max_length=50,
        unique=True,
        db_column='codigo',
        help_text='Código único de identificación de la maquinaria'
    )
    nombre = models.CharField(
        max_length=200,
        db_column='nombre',
        help_text='Nombre o descripción de la maquinaria'
    )
    
    # Relación con empresa
    empresa = models.CharField(
        max_length=20,
        choices=EmpresaMaquinaria.choices,
        db_column='empresa',
        verbose_name='Empresa',
        help_text='Empresa a la que pertenece la maquinaria'
    )
    
    # Tipo y características
    tipo_maquinaria = models.CharField(
        max_length=30,
        choices=TipoMaquinaria.choices,
        db_column='tipo_maquinaria',
        verbose_name='Tipo de Maquinaria'
    )
    marca = models.CharField(max_length=100, db_column='marca')
    modelo = models.CharField(max_length=100, db_column='modelo')
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column='numero_serie',
        help_text='Número de serie del fabricante'
    )
    año_fabricacion = models.IntegerField(
        blank=True,
        null=True,
        db_column='año_fabricacion',
        validators=[MinValueValidator(1900)],
        help_text='Año de fabricación'
    )
    
    # Estado y mantenimiento
    estado_actual = models.CharField(
        max_length=20,
        db_column='estado_actual',
        help_text='Estado actual: operativa, en mantenimiento, fuera de servicio, etc.'
    )
    fecha_ultimo_mantenimiento = models.DateField(
        blank=True,
        null=True,
        db_column='fecha_ultimo_mantenimiento'
    )
    fecha_proximo_mantenimiento = models.DateField(
        blank=True,
        null=True,
        db_column='fecha_proximo_mantenimiento'
    )
    
    # Métricas de uso
    horas_operacion = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        db_column='horas_operacion',
        help_text='Horas totales de operación'
    )
    kilometraje = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        db_column='kilometraje',
        help_text='Kilometraje (si aplica)'
    )
    
    # Documentación y seguros
    seguro_vigente = models.BooleanField(
        default=True,
        db_column='seguro_vigente',
        help_text='Indica si el seguro está vigente'
    )
    documentacion_vigente = models.BooleanField(
        default=True,
        db_column='documentacion_vigente',
        help_text='Indica si la documentación está vigente'
    )
    
    # Información adicional
    ubicacion_actual = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        db_column='ubicacion_actual',
        help_text='Ubicación actual de la maquinaria'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        db_column='observaciones'
    )
    
    # Control
    activo = models.BooleanField(default=True, db_column='activo')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'maquinaria'
        verbose_name = 'Maquinaria'
        verbose_name_plural = 'Maquinarias'
        ordering = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['codigo'], name='idx_maquinaria_codigo'),
            models.Index(fields=['empresa'], name='idx_maquinaria_empresa'),
            models.Index(fields=['tipo_maquinaria'], name='idx_maquinaria_tipo'),
            models.Index(fields=['marca', 'modelo'], name='idx_maquinaria_marca_modelo'),
            models.Index(fields=['estado_actual'], name='idx_maquinaria_estado'),
            models.Index(fields=['fecha_proximo_mantenimiento'], name='idx_maquinaria_prox_mant'),
            models.Index(fields=['activo'], name='idx_maquinaria_activo'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(horas_operacion__gte=0),
                name='chk_maquinaria_horas_nonneg'
            ),
            models.CheckConstraint(
                check=models.Q(kilometraje__gte=0),
                name='chk_maquinaria_km_nonneg'
            ),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.get_empresa_display()})"
    
    def clean(self):
        """
        Validación personalizada
        """
        from django.core.exceptions import ValidationError
        
        # Validar que la empresa sea válida
        if self.empresa not in [choice[0] for choice in EmpresaMaquinaria.choices]:
            raise ValidationError({
                'empresa': 'La empresa seleccionada no es válida.'
            })


class TipoMantenimiento(models.TextChoices):
    """
    Tipos de mantenimiento disponibles
    """
    PREVENTIVO = 'PREVENTIVO', 'Preventivo'
    CORRECTIVO = 'CORRECTIVO', 'Correctivo'
    EMERGENCIA = 'EMERGENCIA', 'Emergencia'
    LEGAL_INSPECCION = 'LEGAL_INSPECCION', 'Legal / Inspección'


class PrioridadOrden(models.TextChoices):
    """
    Prioridades para órdenes de trabajo
    """
    BAJA = 'BAJA', 'Baja'
    MEDIA = 'MEDIA', 'Media'
    ALTA = 'ALTA', 'Alta'
    URGENTE = 'URGENTE', 'Urgente'


class EstadoOrden(models.TextChoices):
    """
    Estados de la orden de trabajo
    """
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
    COMPLETADA = 'COMPLETADA', 'Completada'
    CANCELADA = 'CANCELADA', 'Cancelada'
    VENCIDA = 'VENCIDA', 'Vencida'


class OrdenTrabajo(models.Model):
    """
    Modelo para órdenes de trabajo de mantenimiento
    """
    # Identificación
    codigo_orden = models.CharField(
        max_length=20,
        unique=True,
        db_column='codigo_orden',
        help_text='Código único de la orden de trabajo'
    )
    
    # Relaciones principales
    maquinaria = models.ForeignKey(
        Maquinaria,
        on_delete=models.PROTECT,
        related_name='ordenes_trabajo',
        db_column='maquinaria_id',
        help_text='Maquinaria a la que aplica el mantenimiento'
    )
    tecnico = models.ForeignKey(
        'planillas.Empleado',
        on_delete=models.PROTECT,
        related_name='ordenes_asignadas',
        db_column='tecnico_id',
        help_text='Técnico asignado a la orden'
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_creadas',
        db_column='creado_por_id',
        help_text='Usuario que creó la orden'
    )
    
    # Información principal
    tipo_mantenimiento = models.CharField(
        max_length=30,
        choices=TipoMantenimiento.choices,
        db_column='tipo_mantenimiento',
        verbose_name='Tipo de Mantenimiento'
    )
    descripcion_trabajo = models.TextField(
        db_column='descripcion_trabajo',
        help_text='Descripción detallada del trabajo a realizar'
    )
    prioridad = models.CharField(
        max_length=20,
        choices=PrioridadOrden.choices,
        db_column='prioridad',
        verbose_name='Prioridad'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        db_column='observaciones',
        help_text='Observaciones adicionales'
    )
    
    # Repuestos externos como JSON
    repuestos_externos = models.JSONField(
        default=list,
        blank=True,
        db_column='repuestos_externos',
        help_text='Lista de repuestos externos necesarios'
    )
    
    # Programación
    fecha_creacion_orden = models.DateField(
        db_column='fecha_creacion_orden',
        help_text='Fecha de creación de la orden'
    )
    fecha_inicio = models.DateField(
        db_column='fecha_inicio',
        help_text='Fecha de inicio del trabajo'
    )
    fecha_estimada_terminacion = models.DateField(
        db_column='fecha_estimada_terminacion',
        help_text='Fecha estimada de terminación'
    )
    fecha_terminacion_real = models.DateField(
        blank=True,
        null=True,
        db_column='fecha_terminacion_real',
        help_text='Fecha real de terminación'
    )
    
    # Estado y costos
    estado = models.CharField(
        max_length=20,
        choices=EstadoOrden.choices,
        default=EstadoOrden.PENDIENTE,
        db_column='estado',
        verbose_name='Estado'
    )
    progreso = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        db_column='progreso',
        help_text='Porcentaje de progreso (0-100)'
    )
    costo_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='costo_estimado',
        help_text='Costo estimado en Quetzales'
    )
    costo_real = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        db_column='costo_real',
        help_text='Costo real en Quetzales (calculado posteriormente)'
    )
    
    # Control
    activo = models.BooleanField(
        default=True,
        db_column='activo'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'ordenes_trabajo'
        verbose_name = 'Orden de Trabajo'
        verbose_name_plural = 'Órdenes de Trabajo'
        ordering = ['-fecha_creacion_orden', '-created_at']
        indexes = [
            models.Index(fields=['codigo_orden'], name='idx_orden_codigo'),
            models.Index(fields=['maquinaria'], name='idx_orden_maquinaria'),
            models.Index(fields=['tecnico'], name='idx_orden_tecnico'),
            models.Index(fields=['estado'], name='idx_orden_estado'),
            models.Index(fields=['prioridad'], name='idx_orden_prioridad'),
            models.Index(fields=['tipo_mantenimiento'], name='idx_orden_tipo_mant'),
            models.Index(fields=['fecha_inicio'], name='idx_orden_fecha_inicio'),
            models.Index(fields=['fecha_estimada_terminacion'], name='idx_orden_fecha_est'),
            models.Index(fields=['activo'], name='idx_orden_activo'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(progreso__gte=0) & models.Q(progreso__lte=100),
                name='chk_orden_trabajo_progreso'
            ),
        ]

    def __str__(self):
        return f"{self.codigo_orden} - {self.maquinaria.nombre}"
    
    def save(self, *args, **kwargs):
        """
        Genera código de orden automáticamente si no existe
        """
        if not self.codigo_orden:
            from django.utils import timezone
            from datetime import date
            
            # Generar código: OT-YYYY-XXXX
            año = date.today().year
            ultimo = OrdenTrabajo.objects.filter(
                codigo_orden__startswith=f'OT-{año}-'
            ).order_by('-codigo_orden').first()
            
            if ultimo:
                try:
                    ultimo_numero = int(ultimo.codigo_orden.split('-')[-1])
                    nuevo_numero = ultimo_numero + 1
                except:
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            self.codigo_orden = f'OT-{año}-{nuevo_numero:04d}'
        
        super().save(*args, **kwargs)
    
    @property
    def esta_vencida(self):
        """Verifica si la orden está vencida"""
        from datetime import date
        if self.estado in [EstadoOrden.COMPLETADA, EstadoOrden.CANCELADA]:
            return False
        return date.today() > self.fecha_estimada_terminacion
    
    @property
    def dias_restantes(self):
        """Calcula los días restantes hasta la fecha estimada de terminación"""
        from datetime import date
        if self.estado in [EstadoOrden.COMPLETADA, EstadoOrden.CANCELADA]:
            return 0
        delta = self.fecha_estimada_terminacion - date.today()
        return delta.days


class OrdenTrabajoProducto(models.Model):
    """
    Modelo para el detalle de productos de ferretería usados en una orden de trabajo.
    Permite rastrear qué productos se usaron, sus cantidades y si ya se descontaron del inventario.
    """
    orden_trabajo = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.RESTRICT,
        related_name='productos_orden',
        db_column='orden_trabajo_id',
        help_text='Orden de trabajo a la que pertenece este producto'
    )
    producto = models.ForeignKey(
        'ferreteria.Producto',
        on_delete=models.RESTRICT,
        related_name='ordenes_trabajo',
        db_column='producto_id',
        help_text='Producto de ferretería usado en la orden'
    )
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        db_column='cantidad',
        help_text='Cantidad del producto a usar'
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        db_column='precio_unitario',
        help_text='Precio unitario del producto al momento de agregarlo'
    )
    costo_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        db_column='costo_total',
        help_text='Costo total (cantidad x precio_unitario)'
    )
    descontado_inventario = models.BooleanField(
        default=False,
        db_column='descontado_inventario',
        help_text='Indica si ya se descontó del inventario de ferretería'
    )
    movimiento_inventario = models.ForeignKey(
        'ferreteria.MovimientoInventario',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ordenes_trabajo_productos',
        db_column='movimiento_inventario_id',
        help_text='Referencia al movimiento de inventario generado'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'ordenes_trabajo_productos'
        verbose_name = 'Producto de Orden de Trabajo'
        verbose_name_plural = 'Productos de Órdenes de Trabajo'
        ordering = ['orden_trabajo', 'id']
        indexes = [
            models.Index(fields=['orden_trabajo'], name='idx_otp_orden_trabajo'),
            models.Index(fields=['producto'], name='idx_otp_producto'),
            models.Index(fields=['descontado_inventario'], name='idx_otp_descontado'),
        ]

    def __str__(self):
        return f"{self.orden_trabajo.codigo_orden} - {self.producto.nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        """Calcular costo_total automáticamente si hay precio_unitario"""
        if self.precio_unitario and self.cantidad:
            self.costo_total = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)
