# Admin del módulo Taller

from django.contrib import admin
from .models import Maquinaria


@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Maquinaria
    """
    list_display = (
        'codigo', 'nombre', 'empresa', 'tipo_maquinaria',
        'marca', 'modelo', 'estado_actual', 'activo'
    )
    list_filter = ('empresa', 'tipo_maquinaria', 'estado_actual', 'activo', 'seguro_vigente', 'documentacion_vigente')
    search_fields = ('codigo', 'nombre', 'marca', 'modelo', 'numero_serie')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'nombre', 'empresa', 'tipo_maquinaria')
        }),
        ('Características', {
            'fields': ('marca', 'modelo', 'numero_serie', 'año_fabricacion')
        }),
        ('Estado y Mantenimiento', {
            'fields': (
                'estado_actual',
                'fecha_ultimo_mantenimiento',
                'fecha_proximo_mantenimiento',
                'horas_operacion',
                'kilometraje'
            )
        }),
        ('Documentación', {
            'fields': ('seguro_vigente', 'documentacion_vigente')
        }),
        ('Información Adicional', {
            'fields': ('ubicacion_actual', 'observaciones', 'activo')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
