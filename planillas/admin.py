from django.contrib import admin
from .models import Empleado, Asistencia, Nomina, NominaDetalle, PagoNomina


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['codigo_empleado', 'nombres', 'apellidos', 'cargos_display', 'activo']
    list_filter = ['activo', 'cargos', 'area_trabajo']
    search_fields = ['codigo_empleado', 'nombres', 'apellidos', 'dpi']
    ordering = ['codigo_empleado']

    def cargos_display(self, obj):
        return ", ".join(obj.cargos.values_list("nombre", flat=True))
    cargos_display.short_description = "Cargos"


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'fecha', 'hora_entrada', 'hora_salida', 'estado', 'activo']
    list_filter = ['estado', 'activo', 'fecha']
    search_fields = ['empleado__nombres', 'empleado__apellidos', 'empleado__codigo_empleado', 'empleado__dpi']
    date_hierarchy = 'fecha'
    ordering = ['-fecha', '-created_at']
    raw_id_fields = ['empleado', 'usuario']


@admin.register(Nomina)
class NominaAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_periodo', 'fecha_inicio', 'fecha_fin', 'fecha_pago', 'estado', 'created_at']
    list_filter = ['estado', 'tipo_periodo']
    search_fields = ['observaciones']
    date_hierarchy = 'fecha_inicio'
    ordering = ['-fecha_inicio', '-created_at']
    raw_id_fields = ['usuario']


class NominaDetalleInline(admin.TabularInline):
    model = NominaDetalle
    extra = 0
    raw_id_fields = ['empleado']
    readonly_fields = ['salario_neto', 'total_devengado', 'total_descuentos']


@admin.register(NominaDetalle)
class NominaDetalleAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'nomina', 'salario_neto', 'pagado', 'metodo_pago', 'estado', 'activo']
    list_filter = ['pagado', 'estado', 'metodo_pago', 'activo']
    search_fields = ['empleado__nombres', 'empleado__apellidos', 'empleado__codigo_empleado', 'empleado__dpi']
    ordering = ['nomina', 'empleado__codigo_empleado']
    raw_id_fields = ['nomina', 'empleado']


@admin.register(PagoNomina)
class PagoNominaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nomina_detalle', 'forma_pago', 'monto', 'fecha_pago', 'anulado']
    list_filter = ['forma_pago', 'anulado']
    search_fields = ['nomina_detalle__empleado__nombres', 'nomina_detalle__empleado__apellidos', 'numero_cheque']
    date_hierarchy = 'fecha_pago'
    ordering = ['-fecha_pago']
    raw_id_fields = ['nomina_detalle', 'usuario']

