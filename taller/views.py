# Views del módulo Taller

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    Maquinaria, TipoMaquinaria, EmpresaMaquinaria,
    OrdenTrabajo, TipoMantenimiento, PrioridadOrden, EstadoOrden
)
from .serializers import (
    MaquinariaSerializer, MaquinariaListSerializer,
    OrdenTrabajoSerializer, OrdenTrabajoListSerializer,
    OrdenTrabajoCreateUpdateSerializer
)


class MaquinariaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para maquinaria con filtros
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (eliminar)
    """
    queryset = Maquinaria.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilitar paginación, el frontend la maneja

    def get_serializer_class(self):
        if self.action == 'list':
            return MaquinariaListSerializer
        return MaquinariaSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por código, nombre, marca o modelo
        - empresa: FERRETERIA, BLOQUERA, PIEDRINERA o 'todos'
        - tipo_maquinaria: tipo de maquinaria o 'todos'
        - estado: estado de la maquinaria o 'todos'
        - activo: 'activo', 'inactivo' o 'todos'
        """
        queryset = self.queryset

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |
                Q(nombre__icontains=search) |
                Q(marca__icontains=search) |
                Q(modelo__icontains=search)
            )

        # Filtro por empresa
        empresa = self.request.query_params.get('empresa', 'todos')
        if empresa != 'todos':
            queryset = queryset.filter(empresa=empresa)

        # Filtro por tipo de maquinaria
        tipo_maquinaria = self.request.query_params.get('tipo_maquinaria', 'todos')
        if tipo_maquinaria != 'todos':
            queryset = queryset.filter(tipo_maquinaria=tipo_maquinaria)

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado != 'todos':
            queryset = queryset.filter(estado_actual=estado)

        # Filtro por activo
        activo = self.request.query_params.get('activo', 'todos')
        if activo == 'activo':
            queryset = queryset.filter(activo=True)
        elif activo == 'inactivo':
            queryset = queryset.filter(activo=False)

        return queryset.order_by('empresa', 'codigo')

    @action(detail=False, methods=['get'])
    def tipos(self, request):
        """
        Endpoint para obtener los tipos de maquinaria disponibles
        """
        tipos = [
            {'value': choice[0], 'label': choice[1]}
            for choice in TipoMaquinaria.choices
        ]
        return Response(tipos)

    @action(detail=False, methods=['get'])
    def empresas(self, request):
        """
        Endpoint para obtener las empresas disponibles para maquinaria
        """
        empresas = [
            {'value': choice[0], 'label': choice[1]}
            for choice in EmpresaMaquinaria.choices
        ]
        return Response(empresas)


class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Órdenes de Trabajo
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (eliminar)
    """
    queryset = OrdenTrabajo.objects.select_related('maquinaria', 'tecnico', 'creado_por').all()
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return OrdenTrabajoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OrdenTrabajoCreateUpdateSerializer
        return OrdenTrabajoSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por código, descripción, equipo o técnico
        - estado: PENDIENTE, EN_PROGRESO, COMPLETADA, CANCELADA, VENCIDA o 'todos'
        - prioridad: BAJA, MEDIA, ALTA, URGENTE o 'todos'
        - tipo_mantenimiento: PREVENTIVO, CORRECTIVO, EMERGENCIA, LEGAL_INSPECCION o 'todos'
        - maquinaria: ID de maquinaria
        - tecnico: ID de técnico
        - activo: 'activo', 'inactivo' o 'todos'
        - periodo: 'hoy', 'semana', 'mes' o 'todos'
        - vencidas: 'true' para mostrar solo órdenes vencidas
        """
        queryset = self.queryset

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(codigo_orden__icontains=search) |
                Q(descripcion_trabajo__icontains=search) |
                Q(maquinaria__nombre__icontains=search) |
                Q(maquinaria__codigo__icontains=search) |
                Q(tecnico__nombres__icontains=search) |
                Q(tecnico__apellidos__icontains=search)
            )

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado != 'todos':
            queryset = queryset.filter(estado=estado)

        # Filtro por prioridad
        prioridad = self.request.query_params.get('prioridad', 'todos')
        if prioridad != 'todos':
            queryset = queryset.filter(prioridad=prioridad)

        # Filtro por tipo de mantenimiento
        tipo_mantenimiento = self.request.query_params.get('tipo_mantenimiento', 'todos')
        if tipo_mantenimiento != 'todos':
            queryset = queryset.filter(tipo_mantenimiento=tipo_mantenimiento)

        # Filtro por maquinaria
        maquinaria_id = self.request.query_params.get('maquinaria', None)
        if maquinaria_id:
            queryset = queryset.filter(maquinaria_id=maquinaria_id)

        # Filtro por técnico
        tecnico_id = self.request.query_params.get('tecnico', None)
        if tecnico_id:
            queryset = queryset.filter(tecnico_id=tecnico_id)

        # Filtro por activo
        activo = self.request.query_params.get('activo', 'todos')
        if activo == 'activo':
            queryset = queryset.filter(activo=True)
        elif activo == 'inactivo':
            queryset = queryset.filter(activo=False)

        # Filtro por período
        periodo = self.request.query_params.get('periodo', 'todos')
        hoy = date.today()
        if periodo == 'hoy':
            queryset = queryset.filter(fecha_creacion_orden=hoy)
        elif periodo == 'semana':
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            queryset = queryset.filter(fecha_creacion_orden__gte=inicio_semana)
        elif periodo == 'mes':
            inicio_mes = hoy.replace(day=1)
            queryset = queryset.filter(fecha_creacion_orden__gte=inicio_mes)

        # Filtro por vencidas
        vencidas = self.request.query_params.get('vencidas', None)
        if vencidas == 'true':
            queryset = queryset.filter(
                fecha_estimada_terminacion__lt=hoy
            ).exclude(
                estado__in=[EstadoOrden.COMPLETADA, EstadoOrden.CANCELADA]
            )

        return queryset.order_by('-fecha_creacion_orden', '-created_at')

    def perform_destroy(self, instance):
        """
        En lugar de eliminar, desactivar la orden (soft delete)
        """
        instance.activo = False
        instance.save()

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint para obtener estadísticas de órdenes de trabajo
        """
        queryset = self.get_queryset().filter(activo=True)
        hoy = date.today()
        
        # Estadísticas generales
        total = queryset.count()
        pendientes = queryset.filter(estado=EstadoOrden.PENDIENTE).count()
        en_progreso = queryset.filter(estado=EstadoOrden.EN_PROGRESO).count()
        completadas = queryset.filter(estado=EstadoOrden.COMPLETADA).count()
        canceladas = queryset.filter(estado=EstadoOrden.CANCELADA).count()
        
        # Vencidas (no completadas/canceladas y fecha pasada)
        vencidas = queryset.filter(
            fecha_estimada_terminacion__lt=hoy
        ).exclude(
            estado__in=[EstadoOrden.COMPLETADA, EstadoOrden.CANCELADA]
        ).count()
        
        # Costo total estimado
        costo_total = queryset.aggregate(
            total=Sum('costo_estimado')
        )['total'] or 0
        
        # Por prioridad
        por_prioridad = {
            'BAJA': queryset.filter(prioridad=PrioridadOrden.BAJA).count(),
            'MEDIA': queryset.filter(prioridad=PrioridadOrden.MEDIA).count(),
            'ALTA': queryset.filter(prioridad=PrioridadOrden.ALTA).count(),
            'URGENTE': queryset.filter(prioridad=PrioridadOrden.URGENTE).count(),
        }
        
        return Response({
            'total': total,
            'pendientes': pendientes,
            'enProgreso': en_progreso,
            'completadas': completadas,
            'canceladas': canceladas,
            'vencidas': vencidas,
            'costoTotal': float(costo_total),
            'porPrioridad': por_prioridad,
        })

    @action(detail=False, methods=['get'])
    def tipos_mantenimiento(self, request):
        """
        Endpoint para obtener los tipos de mantenimiento disponibles
        """
        tipos = [
            {'value': choice[0], 'label': choice[1]}
            for choice in TipoMantenimiento.choices
        ]
        return Response(tipos)

    @action(detail=False, methods=['get'])
    def prioridades(self, request):
        """
        Endpoint para obtener las prioridades disponibles
        """
        prioridades = [
            {'value': choice[0], 'label': choice[1]}
            for choice in PrioridadOrden.choices
        ]
        return Response(prioridades)

    @action(detail=False, methods=['get'])
    def estados(self, request):
        """
        Endpoint para obtener los estados disponibles
        """
        estados = [
            {'value': choice[0], 'label': choice[1]}
            for choice in EstadoOrden.choices
        ]
        return Response(estados)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint para cambiar el estado de una orden
        """
        orden = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if nuevo_estado not in [choice[0] for choice in EstadoOrden.choices]:
            return Response(
                {'error': 'Estado no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orden.estado = nuevo_estado
        
        # Si se completa, registrar fecha real de terminación
        if nuevo_estado == EstadoOrden.COMPLETADA:
            fecha_terminacion = request.data.get('fecha_terminacion_real')
            if fecha_terminacion:
                # Parsear la fecha/hora enviada desde el frontend
                from datetime import datetime
                try:
                    # El formato puede ser ISO o datetime-local
                    if 'T' in fecha_terminacion:
                        fecha_terminacion = fecha_terminacion.replace('T', ' ')
                    orden.fecha_terminacion_real = fecha_terminacion.split(' ')[0]  # Solo la fecha
                except:
                    orden.fecha_terminacion_real = date.today()
            elif not orden.fecha_terminacion_real:
                orden.fecha_terminacion_real = date.today()
            orden.progreso = 100
        
        orden.save()
        
        serializer = OrdenTrabajoSerializer(orden)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def actualizar_progreso(self, request, pk=None):
        """
        Endpoint para actualizar el progreso de una orden
        """
        orden = self.get_object()
        progreso = request.data.get('progreso')
        
        if progreso is None:
            return Response(
                {'error': 'El campo progreso es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            progreso = int(progreso)
            if progreso < 0 or progreso > 100:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'El progreso debe ser un número entre 0 y 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orden.progreso = progreso
        
        # Si progreso es 100, cambiar estado a completada
        if progreso == 100 and orden.estado != EstadoOrden.COMPLETADA:
            orden.estado = EstadoOrden.COMPLETADA
            orden.fecha_terminacion_real = date.today()
        elif progreso > 0 and orden.estado == EstadoOrden.PENDIENTE:
            orden.estado = EstadoOrden.EN_PROGRESO
        
        orden.save()
        
        serializer = OrdenTrabajoSerializer(orden)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Endpoint para desactivar (soft delete) una orden
        """
        orden = self.get_object()
        orden.activo = False
        orden.save()
        
        return Response({
            'success': True,
            'message': f'Orden {orden.codigo_orden} desactivada correctamente'
        })

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Endpoint para reactivar una orden desactivada
        """
        orden = self.get_object()
        orden.activo = True
        orden.save()
        
        return Response({
            'success': True,
            'message': f'Orden {orden.codigo_orden} activada correctamente'
        })
