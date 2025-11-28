# Modelos del módulo Taller

from django.db import models
from django.core.validators import MinValueValidator


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
