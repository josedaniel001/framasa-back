from django.contrib import admin
from .models import Producto, CategoriaProducto, UnidadMedida, Cliente, Proveedor, MovimientoInventario


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'proveedor', 'precio_venta', 'stock_actual', 'activo')
    list_filter = ('activo', 'categoria', 'proveedor')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('categoria', 'unidad_medida', 'proveedor')
        }),
        ('Precios y Costos', {
            'fields': ('precio_venta', 'costo_unitario')
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
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'abreviatura')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nit', 'telefono', 'email', 'permite_fiado', 'limite_credito', 'saldo_actual', 'activo', 'fecha_registro')
    list_filter = ('activo', 'permite_fiado', 'fecha_registro')
    search_fields = ('nombre', 'nit', 'telefono', 'email')
    ordering = ('nombre',)
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'nit', 'direccion', 'telefono', 'email')
        }),
        ('Fiado (Crédito)', {
            'fields': ('permite_fiado', 'limite_credito', 'saldo_actual', 'credito_disponible', 'puede_comprar_fiado'),
            'description': 'Configuración de crédito para el cliente'
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('fecha_registro', 'created_at', 'updated_at', 'credito_disponible', 'puede_comprar_fiado')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nit', 'telefono', 'email', 'contacto', 'activo', 'fecha_registro')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('nombre', 'nit', 'telefono', 'email', 'contacto')
    ordering = ('nombre',)
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'nit')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'contacto', 'direccion')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('fecha_registro', 'created_at', 'updated_at')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'fecha_movimiento')
    list_filter = ('tipo', 'fecha_movimiento')
    search_fields = ('producto__codigo', 'producto__nombre', 'motivo', 'usuario__username')
    ordering = ('-fecha_movimiento',)
    readonly_fields = ('stock_anterior', 'stock_nuevo', 'fecha_movimiento', 'created_at', 'updated_at')
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('producto', 'tipo', 'cantidad')
        }),
        ('Stock', {
            'fields': ('stock_anterior', 'stock_nuevo')
        }),
        ('Detalles', {
            'fields': ('motivo', 'observaciones', 'usuario')
        }),
        ('Fechas', {
            'fields': ('fecha_movimiento', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """Los movimientos no se pueden eliminar"""
        return False

    def has_change_permission(self, request, obj=None):
        """Los movimientos no se pueden editar después de creados"""
        return False
