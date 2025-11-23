from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings


class Empleado(models.Model):
    """
    Modelo para empleados del sistema
    Compatible con la estructura existente de la tabla
    """
    codigo_empleado = models.CharField(max_length=20, unique=True, db_column='codigo_empleado')
    nombres = models.CharField(max_length=100, db_column='nombres')
    apellidos = models.CharField(max_length=100, db_column='apellidos')
    dpi = models.CharField(max_length=25, unique=True, blank=True, null=True, db_column='dpi')
    nit = models.CharField(max_length=25, blank=True, null=True, db_column='nit')
    telefono = models.CharField(max_length=30, blank=True, null=True, db_column='telefono')
    email = models.EmailField(max_length=150, blank=True, null=True, db_column='email')
    puesto = models.CharField(max_length=100, db_column='puesto')
    area_trabajo = models.CharField(max_length=50, blank=True, null=True, db_column='area_trabajo')
    turno = models.CharField(max_length=50, blank=True, null=True, db_column='turno')
    tipo_contrato = models.CharField(max_length=50, blank=True, null=True, db_column='tipo_contrato')
    salario_base_q = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        db_column='salario_base_q'
    )
    fecha_contratacion = models.DateField(db_column='fecha_contratacion')
    fecha_baja = models.DateField(blank=True, null=True, db_column='fecha_baja')
    usuario_id = models.IntegerField(blank=True, null=True, db_column='usuario_id')
    activo = models.BooleanField(default=True, db_column='activo')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'empleados'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['codigo_empleado']
        indexes = [
            models.Index(fields=['codigo_empleado'], name='idx_empleados_codigo'),
            models.Index(fields=['dpi'], name='idx_empleados_dpi'),
            models.Index(fields=['nombres', 'apellidos'], name='idx_empleados_nombre'),
            models.Index(fields=['puesto'], name='idx_empleados_puesto'),
            models.Index(fields=['activo'], name='idx_empleados_activo'),
        ]

    def __str__(self):
        return f"{self.codigo_empleado} - {self.nombres} {self.apellidos}"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del empleado"""
        return f"{self.nombres} {self.apellidos}"
    
    # Propiedades de compatibilidad para mantener la API consistente
    @property
    def codigo(self):
        """Alias para codigo_empleado"""
        return self.codigo_empleado
    
    @property
    def cedula(self):
        """Alias para dpi"""
        return self.dpi
    
    @property
    def cargo(self):
        """Alias para puesto"""
        return self.puesto
    
    @property
    def salario(self):
        """Alias para salario_base_q"""
        return self.salario_base_q
    
    @property
    def fecha_ingreso(self):
        """Alias para fecha_contratacion"""
        return self.fecha_contratacion
