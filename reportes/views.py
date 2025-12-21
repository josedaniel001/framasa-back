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
from facturacion.models import Factura
from taller.models import OrdenTrabajo

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
        stock_ferreteria = productos_ferreteria.aggregate(
            total=Sum('stock_actual')
        )['total'] or 0
        stock_minimo_ferreteria = productos_ferreteria.aggregate(
            total=Sum('stock_minimo')
        )['total'] or 0
        stock_bajo_ferreteria = productos_ferreteria.filter(
            stock_actual__lte=F('stock_minimo')
        ).count()
        valor_ferreteria = sum(
            p.stock_actual * p.precio_venta for p in productos_ferreteria
        )

        # Bloquera
        productos_bloquera = ProductoBloquera.objects.all()
        total_bloquera = productos_bloquera.count()
        activos_bloquera = productos_bloquera.filter(activo=True).count()
        inactivos_bloquera = productos_bloquera.filter(activo=False).count()
        stock_bloquera = productos_bloquera.aggregate(
            total=Sum('stock_actual')
        )['total'] or 0
        stock_minimo_bloquera = productos_bloquera.aggregate(
            total=Sum('stock_minimo')
        )['total'] or 0
        stock_bajo_bloquera = productos_bloquera.filter(
            stock_actual__lte=F('stock_minimo')
        ).count()
        valor_bloquera = sum(
            p.stock_actual * p.precio_unitario for p in productos_bloquera
        )

        # Piedrinera
        productos_piedrinera = AgregadoPiedrinera.objects.all()
        total_piedrinera = productos_piedrinera.count()
        activos_piedrinera = productos_piedrinera.filter(activo=True).count()
        inactivos_piedrinera = productos_piedrinera.filter(activo=False).count()
        stock_piedrinera = productos_piedrinera.aggregate(
            total=Sum('stock_actual_m3')
        )['total'] or Decimal('0')
        stock_minimo_piedrinera = productos_piedrinera.aggregate(
            total=Sum('stock_minimo_m3')
        )['total'] or Decimal('0')
        stock_bajo_piedrinera = productos_piedrinera.filter(
            stock_actual_m3__lte=F('stock_minimo_m3')
        ).count()
        valor_piedrinera = sum(
            float(p.stock_actual_m3) * float(p.precio_venta_m3) for p in productos_piedrinera
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
                    'stock_total': stock_ferreteria,
                    'stock_minimo_total': stock_minimo_ferreteria,
                    'productos_stock_bajo': stock_bajo_ferreteria,
                    'valor_inventario_estimado': float(valor_ferreteria),
                    'unidades': 'unidades'
                },
                {
                    'empresa': 'bloquera',
                    'total_productos': total_bloquera,
                    'productos_activos': activos_bloquera,
                    'productos_inactivos': inactivos_bloquera,
                    'stock_total': stock_bloquera,
                    'stock_minimo_total': stock_minimo_bloquera,
                    'productos_stock_bajo': stock_bajo_bloquera,
                    'valor_inventario_estimado': float(valor_bloquera),
                    'unidades': 'unidades'
                },
                {
                    'empresa': 'piedrinera',
                    'total_productos': total_piedrinera,
                    'productos_activos': activos_piedrinera,
                    'productos_inactivos': inactivos_piedrinera,
                    'stock_total': float(stock_piedrinera),
                    'stock_minimo_total': float(stock_minimo_piedrinera),
                    'productos_stock_bajo': stock_bajo_piedrinera,
                    'valor_inventario_estimado': valor_piedrinera,
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
        Estadísticas predictivas para productos
        Parámetros: empresa (ferreteria, bloquera, piedrinera), dias_analisis (default: 30)
        """
        empresa = request.query_params.get('empresa', 'todas')
        dias_analisis = int(request.query_params.get('dias_analisis', 30))

        fecha_limite = timezone.now() - timedelta(days=dias_analisis)
        resultados = []

        # Ferretería
        if empresa in ['todas', 'ferreteria']:
            productos = Producto.objects.filter(activo=True)
            for producto in productos:
                movimientos = MovimientoInventario.objects.filter(
                    producto=producto,
                    tipo='SALIDA',
                    fecha_movimiento__gte=fecha_limite
                )

                total_ventas = movimientos.aggregate(
                    total=Sum('cantidad')
                )['total'] or 0

                if total_ventas > 0:
                    promedio_diario = Decimal(str(total_ventas)) / Decimal(str(dias_analisis))
                    promedio_semanal = promedio_diario * 7
                    promedio_mensual = promedio_diario * 30

                    if promedio_diario > 0:
                        dias_restantes = int(producto.stock_actual / promedio_diario)
                    else:
                        dias_restantes = None

                    # Determinar tendencia (comparar primera mitad vs segunda mitad)
                    mitad = dias_analisis // 2
                    primera_mitad = movimientos.filter(
                        fecha_movimiento__gte=fecha_limite + timedelta(days=mitad)
                    ).aggregate(total=Sum('cantidad'))['total'] or 0
                    segunda_mitad = movimientos.filter(
                        fecha_movimiento__lt=fecha_limite + timedelta(days=mitad)
                    ).aggregate(total=Sum('cantidad'))['total'] or 0

                    if primera_mitad > segunda_mitad * 1.1:
                        tendencia = 'creciente'
                    elif segunda_mitad > primera_mitad * 1.1:
                        tendencia = 'decreciente'
                    else:
                        tendencia = 'estable'
                else:
                    promedio_diario = None
                    promedio_semanal = None
                    promedio_mensual = None
                    dias_restantes = None
                    tendencia = None

                resultados.append({
                    'empresa': 'ferreteria',
                    'producto_id': producto.id,
                    'producto_codigo': producto.codigo,
                    'producto_nombre': producto.nombre,
                    'stock_actual': producto.stock_actual,
                    'stock_minimo': producto.stock_minimo,
                    'promedio_ventas_diarias': float(promedio_diario) if promedio_diario else None,
                    'promedio_ventas_semanales': float(promedio_semanal) if promedio_semanal else None,
                    'promedio_ventas_mensuales': float(promedio_mensual) if promedio_mensual else None,
                    'dias_restantes_estimados': dias_restantes,
                    'necesita_reposicion': producto.stock_actual <= producto.stock_minimo,
                    'tendencia': tendencia,
                    'unidades': 'unidades'
                })

        # Bloquera
        if empresa in ['todas', 'bloquera']:
            productos = ProductoBloquera.objects.filter(activo=True)
            for producto in productos:
                movimientos = MovimientoInventarioBloquera.objects.filter(
                    producto=producto,
                    tipo='SALIDA',
                    fecha_movimiento__gte=fecha_limite
                )

                total_ventas = movimientos.aggregate(
                    total=Sum('cantidad')
                )['total'] or 0

                if total_ventas > 0:
                    promedio_diario = Decimal(str(total_ventas)) / Decimal(str(dias_analisis))
                    promedio_semanal = promedio_diario * 7
                    promedio_mensual = promedio_diario * 30

                    if promedio_diario > 0:
                        dias_restantes = int(producto.stock_actual / promedio_diario)
                    else:
                        dias_restantes = None

                    mitad = dias_analisis // 2
                    primera_mitad = movimientos.filter(
                        fecha_movimiento__gte=fecha_limite + timedelta(days=mitad)
                    ).aggregate(total=Sum('cantidad'))['total'] or 0
                    segunda_mitad = movimientos.filter(
                        fecha_movimiento__lt=fecha_limite + timedelta(days=mitad)
                    ).aggregate(total=Sum('cantidad'))['total'] or 0

                    if primera_mitad > segunda_mitad * 1.1:
                        tendencia = 'creciente'
                    elif segunda_mitad > primera_mitad * 1.1:
                        tendencia = 'decreciente'
                    else:
                        tendencia = 'estable'
                else:
                    promedio_diario = None
                    promedio_semanal = None
                    promedio_mensual = None
                    dias_restantes = None
                    tendencia = None

                resultados.append({
                    'empresa': 'bloquera',
                    'producto_id': producto.id,
                    'producto_codigo': producto.codigo,
                    'producto_nombre': producto.nombre,
                    'stock_actual': producto.stock_actual,
                    'stock_minimo': producto.stock_minimo,
                    'promedio_ventas_diarias': float(promedio_diario) if promedio_diario else None,
                    'promedio_ventas_semanales': float(promedio_semanal) if promedio_semanal else None,
                    'promedio_ventas_mensuales': float(promedio_mensual) if promedio_mensual else None,
                    'dias_restantes_estimados': dias_restantes,
                    'necesita_reposicion': producto.stock_actual <= producto.stock_minimo,
                    'tendencia': tendencia,
                    'unidades': 'unidades'
                })

        # Piedrinera
        if empresa in ['todas', 'piedrinera']:
            productos = AgregadoPiedrinera.objects.filter(activo=True)
            for producto in productos:
                movimientos = MovimientoInventarioPiedrinera.objects.filter(
                    producto=producto,
                    tipo='SALIDA',
                    fecha_movimiento__gte=fecha_limite
                )

                total_ventas = movimientos.aggregate(
                    total=Sum('cantidad')
                )['total'] or Decimal('0')

                if total_ventas > 0:
                    promedio_diario = total_ventas / Decimal(str(dias_analisis))
                    promedio_semanal = promedio_diario * 7
                    promedio_mensual = promedio_diario * 30

                    if promedio_diario > 0:
                        dias_restantes = int(float(producto.stock_actual_m3) / float(promedio_diario))
                    else:
                        dias_restantes = None

                    mitad = dias_analisis // 2
                    primera_mitad = movimientos.filter(
                        fecha_movimiento__gte=fecha_limite + timedelta(days=mitad)
                    ).aggregate(total=Sum('cantidad'))['total'] or Decimal('0')
                    segunda_mitad = movimientos.filter(
                        fecha_movimiento__lt=fecha_limite + timedelta(days=mitad)
                    ).aggregate(total=Sum('cantidad'))['total'] or Decimal('0')

                    if primera_mitad > segunda_mitad * Decimal('1.1'):
                        tendencia = 'creciente'
                    elif segunda_mitad > primera_mitad * Decimal('1.1'):
                        tendencia = 'decreciente'
                    else:
                        tendencia = 'estable'
                else:
                    promedio_diario = None
                    promedio_semanal = None
                    promedio_mensual = None
                    dias_restantes = None
                    tendencia = None

                resultados.append({
                    'empresa': 'piedrinera',
                    'producto_id': producto.id,
                    'producto_codigo': producto.codigo,
                    'producto_nombre': producto.nombre,
                    'stock_actual': float(producto.stock_actual_m3),
                    'stock_minimo': float(producto.stock_minimo_m3),
                    'promedio_ventas_diarias': float(promedio_diario) if promedio_diario else None,
                    'promedio_ventas_semanales': float(promedio_semanal) if promedio_semanal else None,
                    'promedio_ventas_mensuales': float(promedio_mensual) if promedio_mensual else None,
                    'dias_restantes_estimados': dias_restantes,
                    'necesita_reposicion': producto.stock_actual_m3 <= producto.stock_minimo_m3,
                    'tendencia': tendencia,
                    'unidades': 'm³'
                })

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
