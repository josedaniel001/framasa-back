from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings
from authentication.models import Usuario


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


class Asistencia(models.Model):
    """
    Modelo para registro de asistencias de empleados
    """
    ESTADO_CHOICES = [
        ('Presente', 'Presente'),
        ('Descanso', 'Descanso'),
        ('Vacaciones', 'Vacaciones'),
        ('Permiso con goce', 'Permiso con goce'),
        ('Permiso sin goce', 'Permiso sin goce'),
        ('Licencia Medica', 'Licencia Medica'),
        ('Ausente', 'Ausente'),
    ]

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.RESTRICT,
        related_name='asistencias',
        db_column='empleado_id'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='asistencias_registradas',
        db_column='usuario_id'
    )
    fecha = models.DateField(db_column='fecha')
    hora_entrada = models.TimeField(blank=True, null=True, db_column='hora_entrada')
    hora_salida = models.TimeField(blank=True, null=True, db_column='hora_salida')
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, db_column='estado')
    fecha_retorno = models.DateField(blank=True, null=True, db_column='fecha_retorno')
    observaciones = models.TextField(blank=True, null=True, db_column='observaciones')
    activo = models.BooleanField(default=True, db_column='activo')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'asistencias'
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        ordering = ['-fecha', '-created_at']
        constraints = [
            # Nota: La unicidad empleado+fecha se maneja con un índice parcial en la BD
            # que solo aplica cuando activo=True (ver migración 0003)
            models.CheckConstraint(
                check=models.Q(fecha_retorno__isnull=True) | models.Q(fecha_retorno__gte=models.F('fecha')),
                name='chk_fecha_retorno'
            ),
        ]
        indexes = [
            models.Index(fields=['empleado', 'fecha'], name='idx_asistencias_empleado_fecha'),
            models.Index(fields=['estado'], name='idx_asistencias_estado'),
        ]

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha} - {self.estado}"

    @property
    def horas_trabajadas(self):
        """Calcula las horas trabajadas si hay entrada y salida"""
        if self.hora_entrada and self.hora_salida:
            from datetime import datetime, timedelta
            entrada = datetime.combine(self.fecha, self.hora_entrada)
            salida = datetime.combine(self.fecha, self.hora_salida)
            diferencia = salida - entrada
            return round(diferencia.total_seconds() / 3600, 2)
        return 0


class Nomina(models.Model):
    """
    Modelo para nóminas (cabecera)
    """
    TIPO_PERIODO_CHOICES = [
        ('MENSUAL', 'Mensual'),
        ('QUINCENAL', 'Quincenal'),
        ('SEMANAL', 'Semanal'),
    ]
    
    ESTADO_CHOICES = [
        ('ABIERTA', 'Abierta'),
        ('CALCULADA', 'Calculada'),
        ('CERRADA', 'Cerrada'),
        ('PAGADA', 'Pagada'),
    ]

    tipo_periodo = models.CharField(
        max_length=20,
        choices=TIPO_PERIODO_CHOICES,
        db_column='tipo_periodo'
    )
    fecha_inicio = models.DateField(db_column='fecha_inicio')
    fecha_fin = models.DateField(db_column='fecha_fin')
    fecha_pago = models.DateField(db_column='fecha_pago')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ABIERTA',
        db_column='estado'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='nominas_creadas',
        db_column='usuario_id'
    )
    observaciones = models.TextField(blank=True, null=True, db_column='observaciones')
    activo = models.BooleanField(default=True, db_column='activo')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'nominas'
        verbose_name = 'Nómina'
        verbose_name_plural = 'Nóminas'
        ordering = ['-fecha_inicio', '-created_at']
        indexes = [
            models.Index(fields=['fecha_inicio', 'fecha_fin'], name='idx_nominas_periodo'),
            models.Index(fields=['estado'], name='idx_nominas_estado'),
            models.Index(fields=['activo'], name='idx_nominas_activo'),
        ]

    def __str__(self):
        return f"Nómina {self.tipo_periodo} ({self.fecha_inicio} - {self.fecha_fin})"

    @property
    def total_empleados(self):
        """Retorna el número de empleados activos (no anulados) en esta nómina"""
        return self.detalles.filter(activo=True).exclude(estado='ANULADO').count()

    @property
    def total_devengado(self):
        """Retorna el total devengado de la nómina (excluyendo anulados)"""
        from django.db.models import Sum
        result = self.detalles.filter(activo=True).exclude(estado='ANULADO').aggregate(total=Sum('total_devengado'))
        return result['total'] or 0

    @property
    def total_descuentos(self):
        """Retorna el total de descuentos de la nómina (excluyendo anulados)"""
        from django.db.models import Sum
        result = self.detalles.filter(activo=True).exclude(estado='ANULADO').aggregate(total=Sum('total_descuentos'))
        return result['total'] or 0

    @property
    def total_neto(self):
        """Retorna el salario neto total de la nómina (excluyendo anulados)"""
        from django.db.models import Sum
        result = self.detalles.filter(activo=True).exclude(estado='ANULADO').aggregate(total=Sum('salario_neto'))
        return result['total'] or 0

    @property
    def total_pagado(self):
        """Retorna cuántos empleados ya fueron pagados (excluyendo anulados)"""
        return self.detalles.filter(activo=True, pagado=True).exclude(estado='ANULADO').count()

    @property
    def total_pendientes(self):
        """Retorna cuántos empleados están pendientes por pagar (excluyendo anulados)"""
        return self.detalles.filter(activo=True, pagado=False).exclude(estado='ANULADO').count()

    @property
    def total_anulados(self):
        """Retorna cuántos empleados fueron anulados"""
        return self.detalles.filter(activo=True, estado='ANULADO').count()


class NominaDetalle(models.Model):
    """
    Modelo para detalle de nómina (línea por empleado)
    """
    ESTADO_CHOICES = [
        ('CALCULADO', 'Calculado'),
        ('AJUSTADO', 'Ajustado'),
        ('PAGADO', 'Pagado'),
        ('ANULADO', 'Anulado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('CHEQUE', 'Cheque'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]

    nomina = models.ForeignKey(
        Nomina,
        on_delete=models.CASCADE,
        related_name='detalles',
        db_column='nomina_id'
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.RESTRICT,
        related_name='nominas_detalle',
        db_column='empleado_id'
    )
    
    # Resumen de días
    dias_trabajados = models.IntegerField(default=0, db_column='dias_trabajados')
    dias_descanso = models.IntegerField(default=0, db_column='dias_descanso')
    dias_vacaciones = models.IntegerField(default=0, db_column='dias_vacaciones')
    dias_permiso_con_goce = models.IntegerField(default=0, db_column='dias_permiso_con_goce')
    dias_permiso_sin_goce = models.IntegerField(default=0, db_column='dias_permiso_sin_goce')
    dias_licencia_medica = models.IntegerField(default=0, db_column='dias_licencia_medica')
    dias_ausente = models.IntegerField(default=0, db_column='dias_ausente')
    
    # Copia del salario para historial
    salario_base_mensual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column='salario_base_mensual'
    )
    salario_base_periodo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column='salario_base_periodo'
    )
    
    # Devengado
    salario_base_devengado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column='salario_base_devengado'
    )
    horas_extra = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        db_column='horas_extra'
    )
    monto_horas_extra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column='monto_horas_extra'
    )
    bonificaciones = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column='bonificaciones'
    )
    
    # Deducciones
    igss = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column='igss'
    )
    isr = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column='isr'
    )
    otros_descuentos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column='otros_descuentos'
    )
    
    # Totales
    total_devengado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column='total_devengado'
    )
    total_descuentos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column='total_descuentos'
    )
    salario_neto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column='salario_neto'
    )
    
    # Estado de la línea
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='CALCULADO',
        db_column='estado'
    )
    
    # Resumen de pago
    pagado = models.BooleanField(default=False, db_column='pagado')
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        blank=True,
        null=True,
        db_column='metodo_pago'
    )
    fecha_pagado = models.DateTimeField(blank=True, null=True, db_column='fecha_pagado')
    
    observaciones = models.TextField(blank=True, null=True, db_column='observaciones')
    activo = models.BooleanField(default=True, db_column='activo')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'nomina_detalle'
        verbose_name = 'Detalle de Nómina'
        verbose_name_plural = 'Detalles de Nómina'
        ordering = ['nomina', 'empleado__codigo_empleado']
        indexes = [
            models.Index(fields=['nomina'], name='idx_nomina_detalle_nomina'),
            models.Index(fields=['empleado'], name='idx_nomina_detalle_empleado'),
            models.Index(fields=['pagado'], name='idx_nomina_detalle_pagado'),
        ]

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.nomina}"


class PagoNomina(models.Model):
    """
    Modelo para registrar pagos de nómina
    """
    FORMA_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('CHEQUE', 'Cheque'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]

    nomina_detalle = models.ForeignKey(
        NominaDetalle,
        on_delete=models.RESTRICT,
        related_name='pagos',
        db_column='nomina_detalle_id'
    )
    forma_pago = models.CharField(
        max_length=20,
        choices=FORMA_PAGO_CHOICES,
        db_column='forma_pago'
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column='monto'
    )
    moneda = models.CharField(
        max_length=3,
        default='GTQ',
        db_column='moneda'
    )
    fecha_pago = models.DateTimeField(auto_now_add=True, db_column='fecha_pago')
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='pagos_nomina_realizados',
        db_column='usuario_id'
    )
    
    # Datos específicos para cheque
    banco = models.CharField(max_length=100, blank=True, null=True, db_column='banco')
    numero_cheque = models.CharField(max_length=50, blank=True, null=True, db_column='numero_cheque')
    cuenta_bancaria = models.CharField(max_length=50, blank=True, null=True, db_column='cuenta_bancaria')
    fecha_cobro = models.DateField(blank=True, null=True, db_column='fecha_cobro')
    
    # Anulación
    anulado = models.BooleanField(default=False, db_column='anulado')
    motivo_anulacion = models.TextField(blank=True, null=True, db_column='motivo_anulacion')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'pagos_nomina'
        verbose_name = 'Pago de Nómina'
        verbose_name_plural = 'Pagos de Nómina'
        ordering = ['-fecha_pago']
        indexes = [
            models.Index(fields=['nomina_detalle'], name='idx_pagos_nomina_detalle'),
            models.Index(fields=['forma_pago'], name='idx_pagos_nomina_forma'),
        ]

    def __str__(self):
        return f"Pago {self.forma_pago} - {self.monto} GTQ - {self.nomina_detalle.empleado.nombre_completo}"
