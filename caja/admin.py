from django.contrib import admin
from .models import MovimientoCaja, MovimientoCajaDetalle


@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ('id', 'empresa', 'tipo', 'fecha_hora', 'referencia', 'total', 'estado', 'created_at')
    list_filter = ('empresa', 'tipo', 'estado', 'fecha_hora')
    search_fields = ('referencia', 'descripcion')
    date_hierarchy = 'fecha_hora'
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-fecha_hora',)


@admin.register(MovimientoCajaDetalle)
class MovimientoCajaDetalleAdmin(admin.ModelAdmin):
    list_display = ('id', 'movimiento', 'producto_nombre', 'cantidad', 'costo_total', 'created_at')
    list_filter = ('movimiento__empresa', 'movimiento__tipo', 'created_at')
    search_fields = ('producto_nombre', 'movimiento__referencia')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
