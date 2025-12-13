# Admin del módulo Taller

from django.contrib import admin
from .models import Maquinaria, OrdenTrabajo, OrdenTrabajoProducto


class OrdenTrabajoProductoInline(admin.TabularInline):
    """
    Inline para mostrar productos dentro de una orden de trabajo
    """
    model = OrdenTrabajoProducto
    extra = 0
    readonly_fields = ('costo_total', 'descontado_inventario', 'movimiento_inventario', 'created_at', 'updated_at')
    fields = ('producto', 'cantidad', 'precio_unitario', 'costo_total', 'descontado_inventario', 'movimiento_inventario')
    raw_id_fields = ['producto']


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


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Órdenes de Trabajo
    """
    list_display = (
        'codigo_orden', 'maquinaria', 'tecnico', 'tipo_mantenimiento',
        'prioridad', 'estado', 'progreso', 'fecha_inicio', 
        'fecha_estimada_terminacion', 'costo_estimado', 'activo'
    )
    list_filter = (
        'estado', 'prioridad', 'tipo_mantenimiento', 'activo',
        'fecha_inicio', 'fecha_estimada_terminacion'
    )
    search_fields = (
        'codigo_orden', 'maquinaria__nombre', 'maquinaria__codigo',
        'tecnico__nombre', 'tecnico__apellido', 'descripcion_trabajo'
    )
    readonly_fields = ('created_at', 'updated_at', 'codigo_orden')
    autocomplete_fields = ['maquinaria']
    raw_id_fields = ['tecnico', 'creado_por']
    date_hierarchy = 'fecha_creacion_orden'
    inlines = [OrdenTrabajoProductoInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo_orden', 'maquinaria', 'tecnico', 'creado_por')
        }),
        ('Información del Trabajo', {
            'fields': ('tipo_mantenimiento', 'descripcion_trabajo', 'prioridad', 'observaciones')
        }),
        ('Repuestos Externos', {
            'fields': ('repuestos_externos',),
            'classes': ('collapse',)
        }),
        ('Programación', {
            'fields': (
                'fecha_creacion_orden', 'fecha_inicio',
                'fecha_estimada_terminacion', 'fecha_terminacion_real'
            )
        }),
        ('Estado y Costos', {
            'fields': ('estado', 'progreso', 'costo_estimado', 'costo_real')
        }),
        ('Control', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('maquinaria', 'tecnico', 'creado_por')


@admin.register(OrdenTrabajoProducto)
class OrdenTrabajoProductoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Productos de Órdenes de Trabajo
    """
    list_display = (
        'orden_trabajo', 'producto', 'cantidad', 'precio_unitario',
        'costo_total', 'descontado_inventario', 'movimiento_inventario'
    )
    list_filter = ('descontado_inventario', 'created_at')
    search_fields = (
        'orden_trabajo__codigo_orden', 'producto__nombre', 'producto__codigo'
    )
    readonly_fields = ('costo_total', 'created_at', 'updated_at')
    autocomplete_fields = ['producto', 'movimiento_inventario']
    raw_id_fields = ['orden_trabajo']
    
    fieldsets = (
        ('Relación', {
            'fields': ('orden_trabajo', 'producto')
        }),
        ('Cantidades y Costos', {
            'fields': ('cantidad', 'precio_unitario', 'costo_total')
        }),
        ('Inventario', {
            'fields': ('descontado_inventario', 'movimiento_inventario')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'orden_trabajo', 'producto', 'movimiento_inventario'
        )
