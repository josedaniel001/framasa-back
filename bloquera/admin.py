from django.contrib import admin
from .models import ProductoBloquera, MovimientoInventarioBloquera


@admin.register(ProductoBloquera)
class ProductoBloqueraAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo_bloque', 'precio_unitario', 'stock_actual', 'stock_minimo', 'activo', 'created_at')
    list_filter = ('activo', 'tipo_bloque', 'created_at')
    search_fields = ('codigo', 'nombre', 'tipo_bloque', 'dimensiones')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Tipo y Dimensiones', {
            'fields': ('tipo_bloque', 'dimensiones')
        }),
        ('Precios', {
            'fields': ('precio_unitario', 'costo_produccion')
        }),
        ('Inventario', {
            'fields': ('stock_actual', 'stock_minimo')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MovimientoInventarioBloquera)
class MovimientoInventarioBloqueraAdmin(admin.ModelAdmin):
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
