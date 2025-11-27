from django.contrib import admin
from django.utils.html import format_html
from .models import Factura, DetalleFactura, Pago, Cotizacion, DetalleCotizacion


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_factura', 'cliente', 'empresa', 'get_estado_display',
        'total', 'total_pagado', 'saldo_pendiente', 'fecha_factura', 'usuario'
    )
    list_filter = ('estado', 'empresa', 'fecha_factura')
    search_fields = ('numero_factura', 'cliente__nombre', 'cliente__nit')
    readonly_fields = (
        'numero_factura', 'subtotal', 'total', 'total_pagado',
        'saldo_pendiente', 'estado', 'created_at', 'updated_at'
    )
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_factura', 'empresa', 'cliente', 'usuario')
        }),
        ('Totales', {
            'fields': ('subtotal', 'descuento', 'total', 'total_pagado', 'saldo_pendiente', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_factura', 'fecha_vencimiento')
        }),
        ('Información Adicional', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente', 'usuario').prefetch_related('detalles', 'pagos')


@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura', 'producto_nombre', 'producto_empresa', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('producto_empresa', 'factura__empresa')
    search_fields = ('factura__numero_factura', 'producto_nombre', 'producto_codigo')
    readonly_fields = ('subtotal', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('factura')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('factura', 'get_tipo_pago_display', 'monto', 'fecha_pago', 'usuario')
    list_filter = ('tipo_pago', 'fecha_pago')
    search_fields = ('factura__numero_factura', 'referencia')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('factura', 'usuario')


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = (
        'numero_cotizacion', 'cliente', 'empresa', 'get_estado_display',
        'total', 'fecha_cotizacion', 'fecha_vencimiento', 'usuario',
        'tiene_factura'
    )
    list_filter = ('estado', 'empresa', 'fecha_cotizacion', 'fecha_vencimiento')
    search_fields = ('numero_cotizacion', 'cliente__nombre', 'cliente__nit')
    readonly_fields = (
        'numero_cotizacion', 'subtotal', 'total', 'estado',
        'fecha_aceptacion', 'factura_generada', 'created_at', 'updated_at'
    )
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_cotizacion', 'empresa', 'cliente', 'usuario')
        }),
        ('Totales', {
            'fields': ('subtotal', 'descuento', 'total', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_cotizacion', 'fecha_vencimiento', 'fecha_aceptacion')
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'condiciones')
        }),
        ('Factura Generada', {
            'fields': ('factura_generada',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente', 'usuario', 'factura_generada').prefetch_related('detalles')
    
    def tiene_factura(self, obj):
        """Indica si la cotización tiene una factura generada"""
        if obj.factura_generada:
            return format_html(
                '<span style="color: green;">✓ Sí</span> - <a href="/admin/facturacion/factura/{}/change/">{}</a>',
                obj.factura_generada.id,
                obj.factura_generada.numero_factura
            )
        return format_html('<span style="color: red;">✗ No</span>')
    tiene_factura.short_description = 'Tiene Factura'


@admin.register(DetalleCotizacion)
class DetalleCotizacionAdmin(admin.ModelAdmin):
    list_display = ('cotizacion', 'producto_nombre', 'producto_empresa', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('producto_empresa', 'cotizacion__empresa')
    search_fields = ('cotizacion__numero_cotizacion', 'producto_nombre', 'producto_codigo')
    readonly_fields = ('subtotal', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cotizacion')
