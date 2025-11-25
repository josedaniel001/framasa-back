from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Factura, DetalleFactura, Pago, EstadoFactura, TipoPago, EmpresaFactura,
    Cotizacion, DetalleCotizacion, EstadoCotizacion
)
from .serializers import (
    FacturaSerializer,
    FacturaCreateSerializer,
    DetalleFacturaSerializer,
    PagoSerializer,
    CotizacionSerializer,
    CotizacionCreateSerializer,
    DetalleCotizacionSerializer
)


class FacturaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar facturas
    """
    queryset = Factura.objects.select_related('cliente', 'usuario').prefetch_related(
        'detalles', 'pagos'
    ).all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FacturaCreateSerializer
        return FacturaSerializer
    
    def get_queryset(self):
        """Filtros opcionales"""
        queryset = self.queryset
        
        # Filtro por cliente
        cliente_id = self.request.query_params.get('cliente', None)
        if cliente_id:
            try:
                queryset = queryset.filter(cliente_id=int(cliente_id))
            except ValueError:
                pass
        
        # Filtro por empresa
        empresa = self.request.query_params.get('empresa', None)
        if empresa:
            queryset = queryset.filter(empresa=empresa)
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            try:
                fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_factura__date__gte=fecha)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_factura__date__lte=fecha)
            except ValueError:
                pass
        
        # Filtro por número de factura
        numero = self.request.query_params.get('numero', None)
        if numero:
            queryset = queryset.filter(numero_factura__icontains=numero)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def agregar_pago(self, request, pk=None):
        """Agregar un pago a la factura"""
        factura = self.get_object()
        
        serializer = PagoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(factura=factura)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def agregar_pagos_multiples(self, request, pk=None):
        """Agregar múltiples pagos a la factura de una vez"""
        factura = self.get_object()
        pagos_data = request.data.get('pagos', [])
        
        if not pagos_data:
            return Response(
                {'error': 'Debe proporcionar al menos un pago'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que la suma de pagos no exceda el saldo
        total_pagos = sum(Decimal(str(p['monto'])) for p in pagos_data)
        if total_pagos > factura.saldo_pendiente:
            return Response(
                {'error': f'El total de pagos ({total_pagos:.2f}) excede el saldo pendiente ({factura.saldo_pendiente:.2f})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar fiado
        for pago_data in pagos_data:
            if pago_data.get('tipo_pago') == TipoPago.FIADO:
                monto_fiado = Decimal(str(pago_data['monto']))
                puede, mensaje = factura.puede_pagar_fiado(monto_fiado)
                if not puede:
                    return Response(
                        {'error': f'Error en pago a fiado: {mensaje}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Crear pagos
        pagos_creados = []
        for pago_data in pagos_data:
            serializer = PagoSerializer(data=pago_data, context={'request': request})
            if serializer.is_valid():
                pago = serializer.save(factura=factura)
                pagos_creados.append(serializer.data)
            else:
                return Response(
                    {'error': f'Error en pago: {serializer.errors}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Refrescar factura
        factura.refresh_from_db()
        factura_serializer = FacturaSerializer(factura)
        
        return Response({
            'factura': factura_serializer.data,
            'pagos_creados': pagos_creados
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anular una factura"""
        factura = self.get_object()
        
        if factura.estado == EstadoFactura.ANULADA:
            return Response(
                {'error': 'La factura ya está anulada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if factura.total_pagado > 0:
            return Response(
                {'error': 'No se puede anular una factura con pagos registrados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Revertir movimientos de inventario
        for detalle in factura.detalles.all():
            # Obtener el producto según el tipo
            if detalle.producto_empresa == 'FERRETERIA':
                from ferreteria.models import Producto, MovimientoInventario, TipoMovimiento
                try:
                    producto = Producto.objects.get(codigo=detalle.producto_codigo)
                    MovimientoInventario.objects.create(
                        producto=producto,
                        tipo=TipoMovimiento.ENTRADA,
                        cantidad=int(detalle.cantidad),
                        motivo=f"Anulación de factura {factura.numero_factura}",
                        usuario=request.user
                    )
                except Producto.DoesNotExist:
                    pass
            elif detalle.producto_empresa == 'BLOQUERA':
                from bloquera.models import ProductoBloquera, MovimientoInventarioBloquera, TipoMovimientoBloquera
                try:
                    producto = ProductoBloquera.objects.get(codigo=detalle.producto_codigo)
                    MovimientoInventarioBloquera.objects.create(
                        producto=producto,
                        tipo=TipoMovimientoBloquera.ENTRADA,
                        cantidad=int(detalle.cantidad),
                        motivo=f"Anulación de factura {factura.numero_factura}",
                        usuario=request.user
                    )
                except ProductoBloquera.DoesNotExist:
                    pass
            elif detalle.producto_empresa == 'PIEDRINERA':
                from piedrinera.models import AgregadoPiedrinera, MovimientoInventarioPiedrinera, TipoMovimientoPiedrinera
                try:
                    producto = AgregadoPiedrinera.objects.get(codigo=detalle.producto_codigo)
                    MovimientoInventarioPiedrinera.objects.create(
                        producto=producto,
                        tipo=TipoMovimientoPiedrinera.ENTRADA,
                        cantidad=detalle.cantidad,
                        motivo=f"Anulación de factura {factura.numero_factura}",
                        usuario=request.user
                    )
                except AgregadoPiedrinera.DoesNotExist:
                    pass
        
        factura.estado = EstadoFactura.ANULADA
        factura.save()
        
        return Response(FacturaSerializer(factura).data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de facturación"""
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        
        queryset = Factura.objects.exclude(estado=EstadoFactura.ANULADA)
        
        if fecha_desde:
            try:
                fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_factura__date__gte=fecha)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_factura__date__lte=fecha)
            except ValueError:
                pass
        
        total_facturas = queryset.count()
        total_ventas = queryset.aggregate(total=Sum('total'))['total'] or Decimal('0')
        total_pagado = queryset.aggregate(total=Sum('total_pagado'))['total'] or Decimal('0')
        total_pendiente = queryset.aggregate(total=Sum('saldo_pendiente'))['total'] or Decimal('0')
        
        por_estado = queryset.values('estado').annotate(
            count=Count('id'),
            total=Sum('total')
        )
        
        por_empresa = queryset.values('empresa').annotate(
            count=Count('id'),
            total=Sum('total')
        )
        
        return Response({
            'total_facturas': total_facturas,
            'total_ventas': float(total_ventas),
            'total_pagado': float(total_pagado),
            'total_pendiente': float(total_pendiente),
            'por_estado': list(por_estado),
            'por_empresa': list(por_empresa)
        })


class PagoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pagos
    """
    queryset = Pago.objects.select_related('factura', 'usuario').all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtros opcionales"""
        queryset = self.queryset
        
        # Filtro por factura
        factura_id = self.request.query_params.get('factura', None)
        if factura_id:
            try:
                queryset = queryset.filter(factura_id=int(factura_id))
            except ValueError:
                pass
        
        # Filtro por tipo de pago
        tipo_pago = self.request.query_params.get('tipo_pago', None)
        if tipo_pago:
            queryset = queryset.filter(tipo_pago=tipo_pago)
        
        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            try:
                fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_pago__date__gte=fecha)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_pago__date__lte=fecha)
            except ValueError:
                pass
        
        return queryset


class CotizacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar cotizaciones
    """
    queryset = Cotizacion.objects.select_related('cliente', 'usuario', 'factura_generada').prefetch_related(
        'detalles'
    ).all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CotizacionCreateSerializer
        return CotizacionSerializer
    
    def get_queryset(self):
        """Filtros opcionales"""
        queryset = self.queryset
        
        # Filtro por cliente
        cliente_id = self.request.query_params.get('cliente', None)
        if cliente_id:
            try:
                queryset = queryset.filter(cliente_id=int(cliente_id))
            except ValueError:
                pass
        
        # Filtro por empresa
        empresa = self.request.query_params.get('empresa', None)
        if empresa:
            queryset = queryset.filter(empresa=empresa)
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            try:
                fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_cotizacion__date__gte=fecha)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_cotizacion__date__lte=fecha)
            except ValueError:
                pass
        
        # Filtro por número de cotización
        numero = self.request.query_params.get('numero', None)
        if numero:
            queryset = queryset.filter(numero_cotizacion__icontains=numero)
        
        # Filtro por vencidas
        vencidas = self.request.query_params.get('vencidas', None)
        if vencidas == 'true':
            from django.utils import timezone
            queryset = queryset.filter(fecha_vencimiento__lt=timezone.now().date())
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def aceptar(self, request, pk=None):
        """Aceptar una cotización"""
        cotizacion = self.get_object()
        
        if cotizacion.estado == EstadoCotizacion.ACEPTADA:
            return Response(
                {'error': 'La cotización ya está aceptada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cotizacion.esta_vencida():
            cotizacion.estado = EstadoCotizacion.VENCIDA
            cotizacion.save()
            return Response(
                {'error': 'La cotización está vencida y no puede ser aceptada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cotizacion.estado = EstadoCotizacion.ACEPTADA
        cotizacion.fecha_aceptacion = timezone.now()
        cotizacion.save()
        
        return Response(CotizacionSerializer(cotizacion).data)
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Rechazar una cotización"""
        cotizacion = self.get_object()
        
        if cotizacion.estado == EstadoCotizacion.RECHAZADA:
            return Response(
                {'error': 'La cotización ya está rechazada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cotizacion.factura_generada:
            return Response(
                {'error': 'No se puede rechazar una cotización que ya tiene una factura generada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cotizacion.estado = EstadoCotizacion.RECHAZADA
        cotizacion.save()
        
        return Response(CotizacionSerializer(cotizacion).data)
    
    @action(detail=True, methods=['post'])
    def enviar(self, request, pk=None):
        """Enviar una cotización al cliente"""
        cotizacion = self.get_object()
        
        if cotizacion.estado != EstadoCotizacion.BORRADOR:
            return Response(
                {'error': 'Solo se pueden enviar cotizaciones en estado borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cotizacion.estado = EstadoCotizacion.ENVIADA
        cotizacion.save()
        
        return Response(CotizacionSerializer(cotizacion).data)
    
    @action(detail=True, methods=['post'])
    def convertir_a_factura(self, request, pk=None):
        """Convertir una cotización aceptada en factura"""
        cotizacion = self.get_object()
        
        # Validar que puede convertirse
        puede, mensaje = cotizacion.puede_convertir_factura()
        if not puede:
            return Response(
                {'error': mensaje},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear factura desde la cotización
        factura_data = {
            'cliente': cotizacion.cliente,
            'empresa': cotizacion.empresa,
            'descuento': cotizacion.descuento,
            'observaciones': f"Generada desde cotización {cotizacion.numero_cotizacion}",
            'usuario': request.user
        }
        
        # Generar número de factura
        empresa = cotizacion.empresa
        prefijo = {
            EmpresaFactura.FERRETERIA: 'FERR',
            EmpresaFactura.BLOQUERA: 'BLOQ',
            EmpresaFactura.PIEDRINERA: 'PIED',
            EmpresaFactura.MIXTA: 'MIXT'
        }.get(empresa, 'FACT')
        
        ultima_factura = Factura.objects.filter(
            numero_factura__startswith=prefijo
        ).order_by('-numero_factura').first()
        
        if ultima_factura:
            try:
                ultimo_numero = int(ultima_factura.numero_factura.replace(prefijo, ''))
                nuevo_numero = ultimo_numero + 1
            except ValueError:
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        
        factura_data['numero_factura'] = f"{prefijo}{nuevo_numero:06d}"
        factura_data['estado'] = EstadoFactura.PENDIENTE
        
        # Crear factura
        factura = Factura.objects.create(**factura_data)
        
        # Crear detalles de factura desde detalles de cotización
        for detalle_cot in cotizacion.detalles.all():
            # Obtener el producto actual
            if detalle_cot.producto_empresa == EmpresaFactura.FERRETERIA:
                from ferreteria.models import Producto, MovimientoInventario, TipoMovimiento
                try:
                    producto = Producto.objects.get(codigo=detalle_cot.producto_codigo, activo=True)
                    content_type = ContentType.objects.get_for_model(Producto)
                    
                    # Crear movimiento de inventario
                    MovimientoInventario.objects.create(
                        producto=producto,
                        tipo=TipoMovimiento.SALIDA,
                        cantidad=int(detalle_cot.cantidad),
                        motivo=f"Venta desde cotización {cotizacion.numero_cotizacion} - Factura {factura.numero_factura}",
                        usuario=request.user
                    )
                except Producto.DoesNotExist:
                    continue
            elif detalle_cot.producto_empresa == EmpresaFactura.BLOQUERA:
                from bloquera.models import ProductoBloquera, MovimientoInventarioBloquera, TipoMovimientoBloquera
                try:
                    producto = ProductoBloquera.objects.get(codigo=detalle_cot.producto_codigo, activo=True)
                    content_type = ContentType.objects.get_for_model(ProductoBloquera)
                    
                    MovimientoInventarioBloquera.objects.create(
                        producto=producto,
                        tipo=TipoMovimientoBloquera.SALIDA,
                        cantidad=int(detalle_cot.cantidad),
                        motivo=f"Venta desde cotización {cotizacion.numero_cotizacion} - Factura {factura.numero_factura}",
                        usuario=request.user
                    )
                except ProductoBloquera.DoesNotExist:
                    continue
            elif detalle_cot.producto_empresa == EmpresaFactura.PIEDRINERA:
                from piedrinera.models import AgregadoPiedrinera, MovimientoInventarioPiedrinera, TipoMovimientoPiedrinera
                try:
                    producto = AgregadoPiedrinera.objects.get(codigo=detalle_cot.producto_codigo, activo=True)
                    content_type = ContentType.objects.get_for_model(AgregadoPiedrinera)
                    
                    MovimientoInventarioPiedrinera.objects.create(
                        producto=producto,
                        tipo=TipoMovimientoPiedrinera.SALIDA,
                        cantidad=detalle_cot.cantidad,
                        motivo=f"Venta desde cotización {cotizacion.numero_cotizacion} - Factura {factura.numero_factura}",
                        usuario=request.user
                    )
                except AgregadoPiedrinera.DoesNotExist:
                    continue
            
            # Crear detalle de factura
            DetalleFactura.objects.create(
                factura=factura,
                content_type=content_type,
                object_id=producto.id,
                producto_codigo=detalle_cot.producto_codigo,
                producto_nombre=detalle_cot.producto_nombre,
                producto_empresa=detalle_cot.producto_empresa,
                cantidad=detalle_cot.cantidad,
                precio_unitario=detalle_cot.precio_unitario,
                descuento=detalle_cot.descuento
            )
        
        # Calcular totales de la factura
        factura.calcular_totales()
        
        # Vincular factura a cotización
        cotizacion.factura_generada = factura
        cotizacion.save()
        
        return Response({
            'cotizacion': CotizacionSerializer(cotizacion).data,
            'factura': FacturaSerializer(factura).data,
            'mensaje': f'Cotización {cotizacion.numero_cotizacion} convertida exitosamente a factura {factura.numero_factura}'
        }, status=status.HTTP_201_CREATED)
