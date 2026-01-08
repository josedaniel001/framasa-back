from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from ferreteria.models import Producto, MovimientoInventario
from bloquera.models import ProductoBloquera, MovimientoInventarioBloquera, OrdenProduccionBloquera
from piedrinera.models import AgregadoPiedrinera, MovimientoInventarioPiedrinera
from facturacion.models import Factura, DetalleFactura, EmpresaFactura
from taller.models import OrdenTrabajo
from django.contrib.contenttypes.models import ContentType

from .serializers import (
    ProductoVendidoSerializer,
    InventarioUnificadoSerializer,
    EstadisticaPredictivaSerializer,
    ReporteInventarioUnificadoSerializer
)


def _tiempo_transcurrido(fecha):
    """
    Función auxiliar para calcular el tiempo transcurrido desde una fecha
    """
    ahora = timezone.now()
    diferencia = ahora - fecha

    if diferencia.days > 0:
        return f"hace {diferencia.days} día{'s' if diferencia.days > 1 else ''}"
    elif diferencia.seconds >= 3600:
        horas = diferencia.seconds // 3600
        return f"hace {horas} hora{'s' if horas > 1 else ''}"
    elif diferencia.seconds >= 60:
        minutos = diferencia.seconds // 60
        return f"hace {minutos} minuto{'s' if minutos > 1 else ''}"
    else:
        return "ahora"


class ReportesViewSet(viewsets.ViewSet):
    """
    ViewSet para reportes unificados del sistema
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def inventario_unificado(self, request):
        """
        Reporte de inventario unificado para las tres empresas
        """
        # Ferretería
        productos_ferreteria = Producto.objects.all()
        total_ferreteria = productos_ferreteria.count()
        activos_ferreteria = productos_ferreteria.filter(activo=True).count()
        inactivos_ferreteria = productos_ferreteria.filter(activo=False).count()
        stock_bajo_ferreteria = productos_ferreteria.filter(
            stock_actual__lte=F('stock_minimo')
        ).count()
        # Valor inventario = costo de compra (costo_unitario * stock_actual)
        valor_ferreteria = sum(
            float(p.stock_actual) * float(p.costo_unitario) for p in productos_ferreteria
        )

        # Bloquera
        productos_bloquera = ProductoBloquera.objects.all()
        total_bloquera = productos_bloquera.count()
        activos_bloquera = productos_bloquera.filter(activo=True).count()
        inactivos_bloquera = productos_bloquera.filter(activo=False).count()
        stock_bajo_bloquera = productos_bloquera.filter(
            stock_actual__lte=F('stock_minimo')
        ).count()
        # Valor inventario = costo de producción (costo_produccion * stock_actual)
        valor_bloquera = sum(
            float(p.stock_actual) * float(p.costo_produccion) for p in productos_bloquera
        )

        # Piedrinera
        productos_piedrinera = AgregadoPiedrinera.objects.all()
        total_piedrinera = productos_piedrinera.count()
        activos_piedrinera = productos_piedrinera.filter(activo=True).count()
        inactivos_piedrinera = productos_piedrinera.filter(activo=False).count()
        stock_bajo_piedrinera = productos_piedrinera.filter(
            stock_actual_m3__lte=F('stock_minimo_m3')
        ).count()
        # Valor inventario = costo de producción (costo_produccion_m3 * stock_actual_m3)
        valor_piedrinera = sum(
            float(p.stock_actual_m3) * float(p.costo_produccion_m3) for p in productos_piedrinera
        )

        # Totales generales
        total_productos = total_ferreteria + total_bloquera + total_piedrinera
        total_activos = activos_ferreteria + activos_bloquera + activos_piedrinera
        total_inactivos = inactivos_ferreteria + inactivos_bloquera + inactivos_piedrinera
        total_stock_bajo = stock_bajo_ferreteria + stock_bajo_bloquera + stock_bajo_piedrinera
        valor_total = Decimal(str(valor_ferreteria)) + Decimal(str(valor_bloquera)) + Decimal(str(valor_piedrinera))

        data = {
            'resumen_general': {
                'total_productos': total_productos,
                'productos_activos': total_activos,
                'productos_inactivos': total_inactivos,
                'productos_stock_bajo': total_stock_bajo,
                'valor_inventario_total': float(valor_total)
            },
            'por_empresa': [
                {
                    'empresa': 'ferreteria',
                    'total_productos': total_ferreteria,
                    'productos_activos': activos_ferreteria,
                    'productos_inactivos': inactivos_ferreteria,
                    'productos_stock_bajo': stock_bajo_ferreteria,
                    'valor_inventario_estimado': float(valor_ferreteria),
                    'unidades': 'unidades'
                },
                {
                    'empresa': 'bloquera',
                    'total_productos': total_bloquera,
                    'productos_activos': activos_bloquera,
                    'productos_inactivos': inactivos_bloquera,
                    'productos_stock_bajo': stock_bajo_bloquera,
                    'valor_inventario_estimado': float(valor_bloquera),
                    'unidades': 'unidades'
                },
                {
                    'empresa': 'piedrinera',
                    'total_productos': total_piedrinera,
                    'productos_activos': activos_piedrinera,
                    'productos_inactivos': inactivos_piedrinera,
                    'productos_stock_bajo': stock_bajo_piedrinera,
                    'valor_inventario_estimado': float(valor_piedrinera),
                    'unidades': 'm³'
                }
            ],
            'total_general': {
                'total_productos': total_productos,
                'productos_activos': total_activos,
                'productos_inactivos': total_inactivos,
                'productos_stock_bajo': total_stock_bajo,
                'valor_inventario_total': float(valor_total)
            }
        }

        serializer = ReporteInventarioUnificadoSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_productos_vendidos(self, request):
        """
        Top de productos más vendidos por empresa
        Parámetros: empresa (ferreteria, bloquera, piedrinera), limit (default: 10), fecha_desde, fecha_hasta
        """
        empresa = request.query_params.get('empresa', 'todas')
        limit = int(request.query_params.get('limit', 10))
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)

        # Filtro de fechas
        filtro_fecha = Q()
        if fecha_desde:
            try:
                fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                filtro_fecha &= Q(fecha_movimiento__date__gte=fecha)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                filtro_fecha &= Q(fecha_movimiento__date__lte=fecha)
            except ValueError:
                pass

        resultados = []

        # Ferretería
        if empresa in ['todas', 'ferreteria']:
            movimientos_ferreteria = MovimientoInventario.objects.filter(
                tipo='SALIDA'
            ).filter(filtro_fecha).values('producto').annotate(
                cantidad_vendida=Sum('cantidad')
            ).order_by('-cantidad_vendida')[:limit]

            for mov in movimientos_ferreteria:
                producto = Producto.objects.get(id=mov['producto'])
                valor_total = mov['cantidad_vendida'] * producto.precio_venta
                resultados.append({
                    'producto_id': producto.id,
                    'producto_codigo': producto.codigo,
                    'producto_nombre': producto.nombre,
                    'empresa': 'ferreteria',
                    'cantidad_vendida': mov['cantidad_vendida'],
                    'unidades': 'unidades',
                    'valor_total': float(valor_total)
                })

        # Bloquera
        if empresa in ['todas', 'bloquera']:
            movimientos_bloquera = MovimientoInventarioBloquera.objects.filter(
                tipo='SALIDA'
            ).filter(filtro_fecha).values('producto').annotate(
                cantidad_vendida=Sum('cantidad')
            ).order_by('-cantidad_vendida')[:limit]

            for mov in movimientos_bloquera:
                producto = ProductoBloquera.objects.get(id=mov['producto'])
                valor_total = mov['cantidad_vendida'] * producto.precio_unitario
                resultados.append({
                    'producto_id': producto.id,
                    'producto_codigo': producto.codigo,
                    'producto_nombre': producto.nombre,
                    'empresa': 'bloquera',
                    'cantidad_vendida': mov['cantidad_vendida'],
                    'unidades': 'unidades',
                    'valor_total': float(valor_total)
                })

        # Piedrinera
        if empresa in ['todas', 'piedrinera']:
            movimientos_piedrinera = MovimientoInventarioPiedrinera.objects.filter(
                tipo='SALIDA'
            ).filter(filtro_fecha).values('producto').annotate(
                cantidad_vendida=Sum('cantidad')
            ).order_by('-cantidad_vendida')[:limit]

            for mov in movimientos_piedrinera:
                producto = AgregadoPiedrinera.objects.get(id=mov['producto'])
                cantidad_decimal = Decimal(str(mov['cantidad_vendida']))
                valor_total = cantidad_decimal * producto.precio_venta_m3
                resultados.append({
                    'producto_id': producto.id,
                    'producto_codigo': producto.codigo,
                    'producto_nombre': producto.nombre,
                    'empresa': 'piedrinera',
                    'cantidad_vendida': float(cantidad_decimal),
                    'unidades': 'm³',
                    'valor_total': float(valor_total)
                })

        # Ordenar por cantidad vendida y limitar
        resultados.sort(key=lambda x: x['cantidad_vendida'], reverse=True)
        resultados = resultados[:limit]

        serializer = ProductoVendidoSerializer(resultados, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas_predictivas(self, request):
        """
        Estadísticas predictivas por producto
        Parámetros: 
        - dias_analisis (default: 30)
        - empresa: 'ferreteria', 'bloquera', 'piedrinera' o 'todas' (default: 'todas')
        Retorna datos por producto con ventas, proyecciones y riesgo de stock
        """
        try:
            dias_analisis = int(request.query_params.get('dias_analisis', 30))
            if dias_analisis <= 0:
                dias_analisis = 30
        except (ValueError, TypeError):
            dias_analisis = 30
        
        empresa_filtro = request.query_params.get('empresa', 'todas')
        if empresa_filtro not in ['ferreteria', 'bloquera', 'piedrinera', 'todas']:
            empresa_filtro = 'todas'
            
        fecha_limite = timezone.now() - timedelta(days=dias_analisis)
        mitad = dias_analisis // 2
        fecha_mitad = fecha_limite + timedelta(days=mitad)
        dias_futuros = 30  # Proyección a 30 días
        
        # Mapeo de empresas
        empresas_map = {
            'ferreteria': ('FERRETERIA', Producto, MovimientoInventario, 'stock_actual'),
            'bloquera': ('BLOQUERA', ProductoBloquera, MovimientoInventarioBloquera, 'stock_actual'),
            'piedrinera': ('PIEDRINERA', AgregadoPiedrinera, MovimientoInventarioPiedrinera, 'stock_actual_m3')
        }
        
        resultados = []
        
        # Determinar qué empresas procesar
        empresas_a_procesar = [empresa_filtro] if empresa_filtro != 'todas' else ['ferreteria', 'bloquera', 'piedrinera']
        
        for empresa_key in empresas_a_procesar:
            try:
                empresa_factura, ProductoModel, MovimientoModel, campo_stock = empresas_map[empresa_key]
                
                # Obtener todos los productos activos de esta empresa
                productos = ProductoModel.objects.filter(activo=True)
                
                # Obtener ContentType para esta empresa
                content_type = ContentType.objects.get_for_model(ProductoModel)
                
                for producto in productos:
                    try:
                        # 1. VENTAS - Suma de subtotal de DetalleFactura para este producto
                        detalles_periodo = DetalleFactura.objects.filter(
                            content_type=content_type,
                            object_id=producto.id,
                            factura__fecha_factura__gte=fecha_limite,
                            factura__estado__in=['PENDIENTE', 'PARCIAL', 'PAGADA']
                        ).exclude(factura__estado='ANULADA')
                        
                        ventas_total = detalles_periodo.aggregate(
                            total=Sum('subtotal')
                        )['total'] or Decimal('0')
                        
                        # Cantidad total vendida (en unidades)
                        cantidad_total_vendida = detalles_periodo.aggregate(
                            total=Sum('cantidad')
                        )['total'] or Decimal('0')
                        
                        # 2. PROMEDIO DIARIO (en Quetzales)
                        prom_diario_q = float(ventas_total) / dias_analisis if dias_analisis > 0 else 0.0
                        
                        # Promedio diario en cantidad (unidades)
                        prom_diario_cantidad = float(cantidad_total_vendida) / dias_analisis if dias_analisis > 0 else 0.0
                        
                        # 3. TENDENCIA - Comparar primera mitad vs segunda mitad (en cantidad)
                        primera_mitad_cantidad = detalles_periodo.filter(
                            factura__fecha_factura__gte=fecha_limite,
                            factura__fecha_factura__lt=fecha_mitad
                        ).aggregate(total=Sum('cantidad'))['total'] or Decimal('0')
                        
                        segunda_mitad_cantidad = detalles_periodo.filter(
                            factura__fecha_factura__gte=fecha_mitad
                        ).aggregate(total=Sum('cantidad'))['total'] or Decimal('0')
                        
                        # Promedios por mitad del período (en cantidad)
                        dias_primera_mitad = mitad if mitad > 0 else 1
                        dias_segunda_mitad = dias_analisis - mitad if (dias_analisis - mitad) > 0 else 1
                        
                        prom_prim = float(primera_mitad_cantidad) / dias_primera_mitad if dias_primera_mitad > 0 else 0.0
                        prom_ult = float(segunda_mitad_cantidad) / dias_segunda_mitad if dias_segunda_mitad > 0 else 0.0
                        
                        # Calcular tendencia
                        if prom_prim > 0:
                            tendencia = (prom_ult - prom_prim) / prom_prim
                        else:
                            tendencia = 0.0
                        
                        # 4. FACTOR según tendencia
                        if tendencia > 0.10:
                            factor = 1.10
                        elif tendencia > 0.05:
                            factor = 1.05
                        elif tendencia < -0.10:
                            factor = 0.90
                        elif tendencia < -0.05:
                            factor = 0.95
                        else:
                            factor = 1.00
                        
                        # 5. PROYECCIÓN 30 DÍAS (en Quetzales)
                        proyeccion_30d = prom_diario_q * dias_futuros * factor
                        
                        # 6. STOCK ACTUAL
                        stock_actual = float(getattr(producto, campo_stock)) if getattr(producto, campo_stock) is not None else 0.0
                        
                        # 7. DÍAS STOCK (usando cantidad vendida por día, no valor en dinero)
                        if prom_diario_cantidad > 0 and stock_actual > 0:
                            dias_stock = int(stock_actual / prom_diario_cantidad)
                        else:
                            dias_stock = None
                        
                        # 8. RIESGO STOCK
                        if dias_stock is None:
                            riesgo_stock = 'Sin datos'
                        elif dias_stock < 10:
                            riesgo_stock = 'Alto'
                        elif dias_stock <= 30:
                            riesgo_stock = 'Medio'
                        else:
                            riesgo_stock = 'Bajo'
                        
                        # 9. RECOMENDACIÓN
                        if riesgo_stock == 'Alto':
                            recomendacion = 'Reponer productos de rotación urgente'
                        elif riesgo_stock == 'Medio':
                            if tendencia > 0.05:
                                recomendacion = 'Aumentar inventario por demanda creciente'
                            else:
                                recomendacion = 'Reponer productos de rotación'
                        elif riesgo_stock == 'Bajo':
                            recomendacion = 'Mantener niveles actuales'
                        else:
                            recomendacion = 'Revisar datos de consumo'
                        
                        resultados.append({
                            'producto_id': producto.id,
                            'producto_codigo': producto.codigo,
                            'producto_nombre': producto.nombre,
                            'empresa': empresa_key,
                            'periodo': dias_analisis,
                            'ventas_q': round(float(ventas_total), 2),
                            'prom_diario_q': round(prom_diario_q, 2),
                            'tendencia_porcentaje': round(tendencia * 100, 1),
                            'proyeccion_30d_q': round(proyeccion_30d, 2),
                            'stock_actual': round(stock_actual, 2) if stock_actual > 0 else None,
                            'dias_stock': dias_stock,
                            'riesgo_stock': riesgo_stock,
                            'recomendacion': recomendacion
                        })
                    except Exception as e:
                        import traceback
                        print(f"Error procesando producto {producto.id}: {str(e)}")
                        print(traceback.format_exc())
                        continue
            except Exception as e:
                import traceback
                print(f"Error procesando empresa {empresa_key}: {str(e)}")
                print(traceback.format_exc())
                continue
        
        serializer = EstadisticaPredictivaSerializer(resultados, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard_metrics(self, request):
        """
        Métricas principales para el Dashboard
        """
        hoy = timezone.now()
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # 1. Ventas del Mes - Suma de totales pagados de facturas del mes actual (excluyendo ANULADAS)
        ventas_mes = Factura.objects.filter(
            fecha_factura__gte=inicio_mes,
            estado__in=['PENDIENTE', 'PARCIAL', 'PAGADA']
        ).exclude(
            estado='ANULADA'
        ).aggregate(
            total=Sum('total_pagado')
        )['total'] or Decimal('0')

        # 2. Órdenes Pendientes - Conteo de órdenes de trabajo y producción con estado PENDIENTE o EN_PROCESO/EN_PROGRESO
        ordenes_taller_pendientes = OrdenTrabajo.objects.filter(
            estado__in=['PENDIENTE', 'EN_PROGRESO']
        ).aggregate(
            total=Count('id')
        )['total'] or 0

        ordenes_bloquera_pendientes = OrdenProduccionBloquera.objects.filter(
            estado__in=['PENDIENTE', 'EN_PROCESO']
        ).aggregate(
            total=Count('id')
        )['total'] or 0

        ordenes_pendientes = ordenes_taller_pendientes + ordenes_bloquera_pendientes

        # 3. Productos en Stock - Conteo de productos con stock_actual > 0 y activos
        productos_stock_ferreteria = Producto.objects.filter(
            activo=True,
            stock_actual__gt=0
        ).aggregate(
            total=Count('id')
        )['total'] or 0

        productos_stock_bloquera = ProductoBloquera.objects.filter(
            activo=True,
            stock_actual__gt=0
        ).aggregate(
            total=Count('id')
        )['total'] or 0

        productos_stock_piedrinera = AgregadoPiedrinera.objects.filter(
            activo=True,
            stock_actual_m3__gt=0
        ).aggregate(
            total=Count('id')
        )['total'] or 0

        productos_stock_total = productos_stock_ferreteria + productos_stock_bloquera + productos_stock_piedrinera

        # 4. Alertas Activas - Conteo de productos con stock_actual <= stock_minimo
        alertas_ferreteria = Producto.objects.filter(
            activo=True,
            stock_actual__lte=F('stock_minimo')
        ).count()

        alertas_bloquera = ProductoBloquera.objects.filter(
            activo=True,
            stock_actual__lte=F('stock_minimo')
        ).count()

        alertas_piedrinera = AgregadoPiedrinera.objects.filter(
            activo=True,
            stock_actual_m3__lte=F('stock_minimo_m3')
        ).count()

        alertas_total = alertas_ferreteria + alertas_bloquera + alertas_piedrinera

        # Calcular cambios porcentuales (comparado con el mes anterior)
        mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
        ventas_mes_anterior = Factura.objects.filter(
            fecha_factura__gte=mes_anterior,
            fecha_factura__lt=inicio_mes,
            estado__in=['PENDIENTE', 'PARCIAL', 'PAGADA']
        ).aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')

        cambio_ventas = 0.0
        if ventas_mes_anterior > 0:
            cambio_ventas = float(((ventas_mes - ventas_mes_anterior) / ventas_mes_anterior) * 100)

        # Órdenes del mes anterior
        ordenes_mes_anterior = OrdenProduccionBloquera.objects.filter(
            created_at__gte=mes_anterior,
            created_at__lt=inicio_mes,
            estado__in=['PENDIENTE', 'EN_PROCESO']
        ).count()

        cambio_ordenes = 0
        if ordenes_mes_anterior > 0:
            cambio_ordenes = ((ordenes_pendientes - ordenes_mes_anterior) / ordenes_mes_anterior) * 100

        # Stock del mes anterior (esto es aproximado, usaríamos snapshots si existieran)
        # Por simplicidad, calculamos un cambio basado en movimientos
        movimientos_entrada_mes = (
            MovimientoInventario.objects.filter(
                tipo='ENTRADA',
                fecha_movimiento__gte=inicio_mes
            ).aggregate(total=Sum('cantidad'))['total'] or 0
        ) + (
            MovimientoInventarioBloquera.objects.filter(
                tipo='ENTRADA',
                fecha_movimiento__gte=inicio_mes
            ).aggregate(total=Sum('cantidad'))['total'] or 0
        )

        movimientos_salida_mes = (
            MovimientoInventario.objects.filter(
                tipo='SALIDA',
                fecha_movimiento__gte=inicio_mes
            ).aggregate(total=Sum('cantidad'))['total'] or 0
        ) + (
            MovimientoInventarioBloquera.objects.filter(
                tipo='SALIDA',
                fecha_movimiento__gte=inicio_mes
            ).aggregate(total=Sum('cantidad'))['total'] or 0
        )

        cambio_stock = 0.0
        if movimientos_entrada_mes + movimientos_salida_mes > 0:
            cambio_stock = ((movimientos_entrada_mes - movimientos_salida_mes) / (productos_stock_total + 1)) * 100

        # Alertas del mes anterior (aproximado)
        alertas_mes_anterior = alertas_total  # Por simplicidad, mantenemos el mismo valor

        cambio_alertas = 0
        if alertas_mes_anterior > 0:
            cambio_alertas = ((alertas_total - alertas_mes_anterior) / alertas_mes_anterior) * 100

        # 5. Actividad Reciente - Últimas 5 actividades del sistema
        actividades_recientes = []

        # Facturas recientes (últimas 24 horas)
        facturas_recientes = Factura.objects.filter(
            fecha_factura__gte=timezone.now() - timedelta(hours=24),
            estado__in=['PENDIENTE', 'PARCIAL', 'PAGADA']
        ).exclude(estado='ANULADA').order_by('-fecha_factura')[:3]

        for factura in facturas_recientes:
            actividades_recientes.append({
                'id': f'factura-{factura.id}',
                'tipo': 'info',
                'titulo': 'Nueva Factura',
                'descripcion': f'Factura {factura.numero_factura} - {factura.cliente.nombre}',
                'monto': f'Q {factura.total_pagado:,.2f}',
                'tiempo': _tiempo_transcurrido(factura.fecha_factura),
                'icono': 'receipt'
            })

        # Órdenes de trabajo recientes (solo PENDIENTE o EN_PROGRESO)
        ordenes_taller_recientes = OrdenTrabajo.objects.filter(
            fecha_creacion_orden__gte=timezone.now() - timedelta(hours=24),
            estado__in=['PENDIENTE', 'EN_PROGRESO']  # Solo órdenes activas
        ).order_by('-fecha_creacion_orden')[:2]

        for orden in ordenes_taller_recientes:
            tipo_actividad = 'warning' if orden.estado == 'PENDIENTE' else 'info'
            actividades_recientes.append({
                'id': f'orden-taller-{orden.id}',
                'tipo': tipo_actividad,
                'titulo': 'Orden de Trabajo',
                'descripcion': f'{orden.maquinaria.nombre} - {orden.get_tipo_mantenimiento_display()}',
                'estado': orden.get_estado_display(),
                'tiempo': _tiempo_transcurrido(orden.fecha_creacion_orden),
                'icono': 'wrench'
            })

        # Órdenes de producción recientes (solo PENDIENTE o EN_PROCESO)
        ordenes_produccion_recientes = OrdenProduccionBloquera.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24),
            estado__in=['PENDIENTE', 'EN_PROCESO']  # Solo órdenes activas
        ).order_by('-created_at')[:2]

        for orden in ordenes_produccion_recientes:
            tipo_actividad = 'warning' if orden.estado == 'PENDIENTE' else 'info'
            actividades_recientes.append({
                'id': f'orden-produccion-{orden.id}',
                'tipo': tipo_actividad,
                'titulo': 'Orden de Producción',
                'descripcion': f'{orden.producto.nombre} - {orden.cantidad_solicitada} unidades',
                'estado': orden.get_estado_display(),
                'tiempo': _tiempo_transcurrido(orden.created_at),
                'icono': 'factory'
            })

        # Productos con stock bajo (alertas)
        productos_stock_bajo = []

        # Ferretería
        productos_bajo_ferreteria = Producto.objects.filter(
            activo=True,
            stock_actual__lte=F('stock_minimo')
        ).order_by('stock_actual')[:2]

        for producto in productos_bajo_ferreteria:
            productos_stock_bajo.append({
                'id': f'stock-ferreteria-{producto.id}',
                'tipo': 'danger',
                'titulo': 'Stock Bajo',
                'descripcion': f'{producto.nombre} - Solo {producto.stock_actual} unidades',
                'empresa': 'Ferretería',
                'tiempo': 'Reciente',
                'icono': 'alert-triangle'
            })

        # Bloquera
        productos_bajo_bloquera = ProductoBloquera.objects.filter(
            activo=True,
            stock_actual__lte=F('stock_minimo')
        ).order_by('stock_actual')[:2]

        for producto in productos_bajo_bloquera:
            productos_stock_bajo.append({
                'id': f'stock-bloquera-{producto.id}',
                'tipo': 'danger',
                'titulo': 'Stock Bajo',
                'descripcion': f'{producto.nombre} - Solo {producto.stock_actual} unidades',
                'empresa': 'Bloquera',
                'tiempo': 'Reciente',
                'icono': 'alert-triangle'
            })

        # Piedrinera
        productos_bajo_piedrinera = AgregadoPiedrinera.objects.filter(
            activo=True,
            stock_actual_m3__lte=F('stock_minimo_m3')
        ).order_by('stock_actual_m3')[:2]

        for producto in productos_bajo_piedrinera:
            productos_stock_bajo.append({
                'id': f'stock-piedrinera-{producto.id}',
                'tipo': 'danger',
                'titulo': 'Stock Bajo',
                'descripcion': f'{producto.nombre} - Solo {producto.stock_actual_m3} m³',
                'empresa': 'Piedrinera',
                'tiempo': 'Reciente',
                'icono': 'alert-triangle'
            })

        # Combinar y ordenar actividades (alertas primero, luego otras actividades)
        actividades_recientes.extend(productos_stock_bajo)
        actividades_recientes.sort(key=lambda x: (
            0 if x['tipo'] == 'danger' else
            1 if x['tipo'] == 'warning' else 2
        ))

        # Limitar a 8 actividades
        actividades_recientes = actividades_recientes[:8]

        data = {
            'ventas_mes': {
                'valor': float(ventas_mes),
                'formateado': f'Q {ventas_mes:,.2f}',
                'cambio_porcentaje': round(cambio_ventas, 1),
                'cambio_formateado': f'{cambio_ventas:+.1f}%',
                'tendencia': 'up' if cambio_ventas >= 0 else 'down'
            },
            'ordenes_pendientes': {
                'valor': ordenes_pendientes,
                'cambio': int(cambio_ordenes),
                'cambio_formateado': f'{cambio_ordenes:+.0f}',
                'tendencia': 'up' if cambio_ordenes >= 0 else 'down'
            },
            'productos_stock': {
                'valor': productos_stock_total,
                'formateado': f'{productos_stock_total:,}',
                'cambio_porcentaje': round(cambio_stock, 1),
                'cambio_formateado': f'{cambio_stock:+.1f}%',
                'tendencia': 'up' if cambio_stock >= 0 else 'down'
            },
            'alertas_activas': {
                'valor': alertas_total,
                'cambio': int(cambio_alertas),
                'cambio_formateado': f'{cambio_alertas:+.0f}',
                'tendencia': 'up' if cambio_alertas >= 0 else 'down'
            },
            'actividades_recientes': actividades_recientes,
            'resumen_por_empresa': {
                'ferreteria': {
                    'ventas_mes': float(Factura.objects.filter(
                        empresa='FERRETERIA',
                        fecha_factura__gte=inicio_mes,
                        estado__in=['PENDIENTE', 'PARCIAL', 'PAGADA']
                    ).exclude(estado='ANULADA').aggregate(total=Sum('total_pagado'))['total'] or Decimal('0')),
                    'productos_stock': productos_stock_ferreteria,
                    'alertas': alertas_ferreteria
                },
                'bloquera': {
                    'ordenes_pendientes': ordenes_bloquera_pendientes,
                    'productos_stock': productos_stock_bloquera,
                    'alertas': alertas_bloquera
                },
                'piedrinera': {
                    'productos_stock': productos_stock_piedrinera,
                    'alertas': alertas_piedrinera
                }
            }
        }

        return Response(data)
