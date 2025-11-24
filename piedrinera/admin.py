from django.contrib import admin
from .models import AgregadoPiedrinera, Camion, MovimientoInventarioPiedrinera


@admin.register(AgregadoPiedrinera)
class AgregadoPiedrineraAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'nombre', 'tipo', 'stock_actual_m3',
        'stock_minimo_m3', 'ubicacion', 'activo', 'created_at'
    )
    list_filter = ('tipo', 'activo')
    search_fields = ('codigo', 'nombre', 'tipo', 'proveedor')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Camion)
class CamionAdmin(admin.ModelAdmin):
    list_display = (
        'placa', 'marca', 'modelo', 'capacidad_m3',
        'estado_actual', 'seguro_vigente', 'activo'
    )
    list_filter = ('estado_actual', 'seguro_vigente', 'activo')
    search_fields = ('placa', 'marca', 'modelo')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MovimientoInventarioPiedrinera)
class MovimientoInventarioPiedrineraAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'producto', 'tipo', 'cantidad',
        'stock_anterior', 'stock_nuevo', 'usuario', 'fecha_movimiento'
    )
    list_filter = ('tipo', 'fecha_movimiento')
    search_fields = ('producto__codigo', 'producto__nombre', 'usuario__username')
    readonly_fields = (
        'producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo',
        'motivo', 'observaciones', 'usuario', 'fecha_movimiento',
        'created_at', 'updated_at'
    )
    fieldsets = (
        ('Movimiento', {
            'fields': ('producto', 'tipo', 'cantidad', 'motivo', 'observaciones')
        }),
        ('Stock', {
            'fields': ('stock_anterior', 'stock_nuevo')
        }),
        ('Auditoría', {
            'fields': ('usuario', 'fecha_movimiento', 'created_at', 'updated_at')
        }),
    )
