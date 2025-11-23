from django.contrib import admin
from .models import Producto, CategoriaProducto, UnidadMedida, Cliente


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_venta', 'stock_actual', 'activo')
    list_filter = ('activo', 'categoria')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)


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
    list_display = ('nombre', 'nit', 'telefono', 'email', 'activo', 'fecha_registro')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('nombre', 'nit', 'telefono', 'email')
    ordering = ('nombre',)
    readonly_fields = ('fecha_registro', 'created_at', 'updated_at')
