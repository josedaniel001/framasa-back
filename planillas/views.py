from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import Empleado, Asistencia, Nomina, NominaDetalle, PagoNomina
from .serializers import (
    EmpleadoSerializer,
    EmpleadoListSerializer,
    EmpleadosStatsSerializer,
    AsistenciaSerializer,
    AsistenciaListSerializer,
    AsistenciaStatsSerializer,
    NominaSerializer,
    NominaListSerializer,
    NominaDetalleSerializer,
    NominaDetalleListSerializer,
    NominaStatsSerializer,
    PagoNominaSerializer,
    ESTADO_FRONTEND_TO_BACKEND
)


class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para empleados con filtros y estadísticas
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (eliminar)
    """
    queryset = Empleado.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilitar paginación, el frontend la maneja

    def get_serializer_class(self):
        if self.action == 'list':
            return EmpleadoListSerializer
        return EmpleadoSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por código, nombres, apellidos, DPI o puesto
        - estado: 'activo', 'inactivo' o 'todos'
        - cargo: puesto específico o 'todos'
        """
        queryset = self.queryset

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(codigo_empleado__icontains=search) |
                Q(nombres__icontains=search) |
                Q(apellidos__icontains=search) |
                Q(dpi__icontains=search) |
                Q(puesto__icontains=search)
            )

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado == 'activo':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivo':
            queryset = queryset.filter(activo=False)

        # Filtro por cargo (puesto)
        cargo = self.request.query_params.get('cargo', 'todos')
        if cargo != 'todos':
            queryset = queryset.filter(puesto=cargo)

        return queryset.order_by('codigo_empleado')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para obtener estadísticas de empleados
        Calcula estadísticas sobre TODOS los empleados, sin filtros
        """
        base_queryset = Empleado.objects.all()

        total_empleados = base_queryset.count()
        empleados_activos = base_queryset.filter(activo=True).count()
        empleados_inactivos = base_queryset.filter(activo=False).count()

        stats = {
            'total_empleados': total_empleados,
            'empleados_activos': empleados_activos,
            'empleados_inactivos': empleados_inactivos,
        }

        serializer = EmpleadosStatsSerializer(stats)
        return Response(serializer.data)


class AsistenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para asistencias con filtros y estadísticas
    Permite GET (listar), POST (crear), GET/{id} (detalle), PUT/{id} (actualizar), DELETE/{id} (eliminar)
    """
    queryset = Asistencia.objects.select_related('empleado').all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilitar paginación, el frontend la maneja

    def get_serializer_class(self):
        if self.action == 'list':
            return AsistenciaListSerializer
        return AsistenciaSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por nombre o código de empleado
        - estado: estado específico o 'todos'
        - fecha: fecha específica (filtro de rango también disponible)
        - fecha_inicio, fecha_fin: rango de fechas
        - empleado_id: ID de empleado específico
        - activo: filtrar solo registros activos (por defecto True)
        """
        queryset = self.queryset

        # Filtro por activo (por defecto solo activos)
        activo = self.request.query_params.get('activo', 'true')
        if activo.lower() == 'true':
            queryset = queryset.filter(activo=True)
        elif activo.lower() == 'false':
            queryset = queryset.filter(activo=False)

        # Búsqueda por texto (nombre o código de empleado)
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(empleado__nombres__icontains=search) |
                Q(empleado__apellidos__icontains=search) |
                Q(empleado__codigo_empleado__icontains=search)
            )

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado != 'todos':
            # Convertir estado de frontend a backend si es necesario
            estado_backend = ESTADO_FRONTEND_TO_BACKEND.get(estado, estado)
            queryset = queryset.filter(estado=estado_backend)

        # Filtro por empleado específico
        empleado_id = self.request.query_params.get('empleado_id', None)
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)

        # Filtro por fecha específica
        fecha = self.request.query_params.get('fecha', None)
        if fecha:
            queryset = queryset.filter(fecha=fecha)

        # Filtro por rango de fechas
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)

        # Filtro predefinido por período (usando zona horaria de Guatemala UTC-6)
        periodo = self.request.query_params.get('periodo', None)
        if periodo:
            import pytz
            from datetime import datetime
            
            # Obtener fecha actual en zona horaria de Guatemala
            guatemala_tz = pytz.timezone('America/Guatemala')
            ahora_guatemala = datetime.now(guatemala_tz)
            hoy = ahora_guatemala.date()
            
            if periodo == 'hoy':
                # Solo registros de hoy
                queryset = queryset.filter(fecha=hoy)
            elif periodo == 'semana':
                # Lunes a domingo de la semana actual
                # weekday(): lunes=0, domingo=6
                inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes
                fin_semana = inicio_semana + timedelta(days=6)  # Domingo
                queryset = queryset.filter(fecha__gte=inicio_semana, fecha__lte=fin_semana)
            elif periodo == 'mes':
                # Todo el mes actual (día 1 hasta último día del mes)
                import calendar
                inicio_mes = hoy.replace(day=1)
                ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]
                fin_mes = hoy.replace(day=ultimo_dia)
                queryset = queryset.filter(fecha__gte=inicio_mes, fecha__lte=fin_mes)

        return queryset.order_by('-fecha', '-created_at')

    def create(self, request, *args, **kwargs):
        """
        Crea una asistencia. Si es Vacaciones o Licencia Médica con fecha de retorno,
        crea automáticamente registros para todo el rango de fechas.
        """
        from datetime import datetime
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtener datos validados
        validated_data = serializer.validated_data
        estado = validated_data.get('estado', '')
        fecha_retorno = validated_data.get('fecha_retorno')
        fecha_inicio = validated_data.get('fecha')
        empleado = validated_data.get('empleado')
        
        # Determinar si es un estado que requiere rango de fechas
        es_estado_con_rango = estado in ['Vacaciones', 'Licencia Medica']
        tiene_fecha_retorno = fecha_retorno is not None
        
        # Asegurar que las fechas sean objetos date para comparación
        if fecha_inicio and fecha_retorno:
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_retorno, str):
                fecha_retorno = datetime.strptime(fecha_retorno, '%Y-%m-%d').date()
        
        fechas_validas = fecha_inicio < fecha_retorno if (fecha_inicio and fecha_retorno) else False
        
        if es_estado_con_rango and tiene_fecha_retorno and fechas_validas:
            # Crear registros para todo el rango de fechas
            registros_creados = []
            fecha_actual = fecha_inicio
            
            while fecha_actual < fecha_retorno:
                # Verificar si ya existe un registro activo para esta fecha
                existe = Asistencia.objects.filter(
                    empleado=empleado,
                    fecha=fecha_actual,
                    activo=True
                ).exists()
                
                if not existe:
                    asistencia = Asistencia.objects.create(
                        empleado=empleado,
                        usuario=request.user,
                        fecha=fecha_actual,
                        hora_entrada=validated_data.get('hora_entrada'),
                        hora_salida=validated_data.get('hora_salida'),
                        estado=estado,
                        fecha_retorno=fecha_retorno,
                        observaciones=validated_data.get('observaciones'),
                        activo=True
                    )
                    registros_creados.append(asistencia)
                
                fecha_actual += timedelta(days=1)
            
            if registros_creados:
                # Retornar el primer registro creado
                result_serializer = self.get_serializer(registros_creados[0])
                return Response(
                    {
                        **result_serializer.data,
                        'registros_creados': len(registros_creados),
                        'mensaje': f'Se crearon {len(registros_creados)} registros de asistencia desde {fecha_inicio} hasta {fecha_retorno - timedelta(days=1)}'
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': 'Ya existen registros activos para todas las fechas en el rango'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Crear un solo registro normal
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """Asigna el usuario actual al crear la asistencia"""
        serializer.save(usuario=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Actualiza una asistencia. Si se cambia a Vacaciones o Licencia Médica con fecha de retorno,
        crea automáticamente registros adicionales para el rango de fechas.
        """
        from datetime import datetime
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Obtener datos validados
        validated_data = serializer.validated_data
        estado = validated_data.get('estado', instance.estado)
        fecha_retorno = validated_data.get('fecha_retorno', instance.fecha_retorno)
        fecha_inicio = validated_data.get('fecha', instance.fecha)
        empleado = validated_data.get('empleado', instance.empleado)
        
        # Asegurar que las fechas sean objetos date para comparación
        if fecha_inicio and fecha_retorno:
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_retorno, str):
                fecha_retorno = datetime.strptime(fecha_retorno, '%Y-%m-%d').date()
        
        # Determinar si es un estado que requiere rango de fechas
        es_estado_con_rango = estado in ['Vacaciones', 'Licencia Medica']
        tiene_fecha_retorno = fecha_retorno is not None
        fechas_validas = fecha_inicio < fecha_retorno if (fecha_inicio and fecha_retorno) else False
        
        if es_estado_con_rango and tiene_fecha_retorno and fechas_validas:
            # Primero actualizar el registro actual
            self.perform_update(serializer)
            
            # Luego crear registros adicionales para los días restantes
            registros_creados = 0
            fecha_actual = fecha_inicio + timedelta(days=1)  # Empezar desde el día siguiente
            
            while fecha_actual < fecha_retorno:
                # Verificar si ya existe un registro activo para esta fecha
                existe = Asistencia.objects.filter(
                    empleado=empleado,
                    fecha=fecha_actual,
                    activo=True
                ).exists()
                
                if not existe:
                    Asistencia.objects.create(
                        empleado=empleado,
                        usuario=request.user,
                        fecha=fecha_actual,
                        hora_entrada=validated_data.get('hora_entrada'),
                        hora_salida=validated_data.get('hora_salida'),
                        estado=estado,
                        fecha_retorno=fecha_retorno,
                        observaciones=validated_data.get('observaciones'),
                        activo=True
                    )
                    registros_creados += 1
                
                fecha_actual += timedelta(days=1)
            
            response_data = serializer.data
            if registros_creados > 0:
                response_data['registros_adicionales'] = registros_creados
                response_data['mensaje'] = f'Se crearon {registros_creados} registros adicionales de asistencia'
            
            return Response(response_data)
        else:
            # Actualización normal
            self.perform_update(serializer)
            return Response(serializer.data)

    def perform_update(self, serializer):
        """Mantiene el usuario original o actualiza si es necesario"""
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete - solo desactiva el registro en lugar de eliminarlo
        """
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def toggle_activo(self, request, pk=None):
        """
        Endpoint para activar/desactivar una asistencia
        """
        asistencia = self.get_object()
        asistencia.activo = not asistencia.activo
        asistencia.save()
        serializer = self.get_serializer(asistencia)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def marcar_salida(self, request, pk=None):
        """
        Endpoint para marcar la hora de salida de una asistencia
        """
        from datetime import datetime
        
        asistencia = self.get_object()
        hora_salida = request.data.get('hora_salida', datetime.now().strftime('%H:%M:%S'))
        asistencia.hora_salida = hora_salida
        asistencia.save()
        serializer = self.get_serializer(asistencia)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para obtener estadísticas de asistencias
        Acepta parámetros: fecha, fecha_inicio, fecha_fin, periodo
        """
        queryset = self.get_queryset()
        
        total_registros = queryset.count()
        presentes = queryset.filter(estado='Presente').count()
        ausentes = queryset.filter(estado='Ausente').count()
        licencias = queryset.filter(estado='Licencia Medica').count()
        vacaciones = queryset.filter(estado='Vacaciones').count()
        descansos = queryset.filter(estado='Descanso').count()
        permisos_con_goce = queryset.filter(estado='Permiso con goce').count()
        permisos_sin_goce = queryset.filter(estado='Permiso sin goce').count()
        
        # Calcular horas totales trabajadas
        horas_totales = 0
        for asistencia in queryset:
            horas_totales += asistencia.horas_trabajadas or 0
        
        # Calcular porcentaje de asistencia
        total_empleados = Empleado.objects.filter(activo=True).count()
        porcentaje_asistencia = (presentes / total_empleados * 100) if total_empleados > 0 else 0

        stats = {
            'total_registros': total_registros,
            'presentes': presentes,
            'ausentes': ausentes,
            'licencias': licencias,
            'vacaciones': vacaciones,
            'descansos': descansos,
            'permisos_con_goce': permisos_con_goce,
            'permisos_sin_goce': permisos_sin_goce,
            'horas_totales': round(horas_totales, 2),
            'porcentaje_asistencia': round(porcentaje_asistencia, 2),
        }

        serializer = AsistenciaStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_empleado(self, request):
        """
        Endpoint para obtener el historial de asistencias de un empleado
        Requiere: empleado_id
        """
        empleado_id = request.query_params.get('empleado_id', None)
        if not empleado_id:
            return Response(
                {'error': 'Se requiere el parámetro empleado_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(empleado_id=empleado_id)
        serializer = AsistenciaListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def empleados_sin_asistencia_hoy(self, request):
        """
        Endpoint para obtener empleados activos sin asistencia hoy,
        o con asistencia desactivada (activo=False)
        """
        from .serializers import EmpleadoListSerializer
        
        hoy = date.today()
        
        # Obtener IDs de empleados con asistencia activa hoy
        empleados_con_asistencia_activa = Asistencia.objects.filter(
            fecha=hoy,
            activo=True
        ).values_list('empleado_id', flat=True)
        
        # Empleados activos que no tienen asistencia activa hoy
        empleados_disponibles = Empleado.objects.filter(
            activo=True
        ).exclude(
            id__in=empleados_con_asistencia_activa
        ).order_by('codigo_empleado')
        
        serializer = EmpleadoListSerializer(empleados_disponibles, many=True)
        return Response(serializer.data)


class NominaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para nóminas con filtros, cálculo automático y estadísticas
    """
    queryset = Nomina.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return NominaListSerializer
        return NominaSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - search: búsqueda por observaciones
        - estado: estado específico o 'todos'
        - tipo_periodo: MENSUAL, QUINCENAL, SEMANAL o 'todos'
        - fecha_inicio, fecha_fin: rango de fechas
        - activo: filtrar por activo (por defecto True)
        """
        queryset = self.queryset

        # Filtro por activo (por defecto solo activas)
        activo = self.request.query_params.get('activo', 'true')
        if activo.lower() == 'true':
            queryset = queryset.filter(activo=True)
        elif activo.lower() == 'false':
            queryset = queryset.filter(activo=False)
        # Si es 'todos', no filtra

        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(observaciones__icontains=search)
            )

        # Filtro por estado
        estado = self.request.query_params.get('estado', 'todos')
        if estado != 'todos':
            queryset = queryset.filter(estado=estado.upper())

        # Filtro por tipo de período
        tipo_periodo = self.request.query_params.get('tipo_periodo', 'todos')
        if tipo_periodo != 'todos':
            queryset = queryset.filter(tipo_periodo=tipo_periodo.upper())

        # Filtro por rango de fechas
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_fin__lte=fecha_fin)

        return queryset.order_by('-fecha_inicio', '-created_at')

    def perform_create(self, serializer):
        """Asigna el usuario actual y calcula la nómina al crear"""
        nomina = serializer.save(usuario=self.request.user)
        # Calcular nómina automáticamente
        self._calcular_nomina(nomina, self.request.data.get('empleadosIncluidos', 'todos'))

    def _calcular_nomina(self, nomina, empleados_incluidos='todos'):
        """
        Calcula la nómina para todos los empleados activos
        basándose en las asistencias del período
        """
        # Obtener empleados según el filtro
        empleados = Empleado.objects.filter(activo=True)
        
        # Filtrar por área de trabajo si se especifica
        if empleados_incluidos and empleados_incluidos != 'todos':
            area_map = {
                'ferreteria': 'Ferretería',
                'bloquera': 'Bloquera',
                'piedrinera': 'Piedrinera',
                'taller': 'Taller',
                'administracion': 'Administración',
                'ventas': 'Ventas',
            }
            area = area_map.get(empleados_incluidos.lower())
            if area:
                empleados = empleados.filter(area_trabajo__iexact=area)

        for empleado in empleados:
            # Obtener asistencias del período (solo activas)
            asistencias = Asistencia.objects.filter(
                empleado=empleado,
                fecha__gte=nomina.fecha_inicio,
                fecha__lte=nomina.fecha_fin,
                activo=True  # Solo asistencias activas
            )
            
            # Estados que NO generan pago ni cuentan como días trabajados
            ESTADOS_SIN_PAGO = ['Ausente', 'Permiso sin goce']
            
            # Contar días por estado individual (para desglose)
            dias_presentes = asistencias.filter(estado='Presente').count()
            dias_descanso = asistencias.filter(estado='Descanso').count()
            dias_vacaciones = asistencias.filter(estado='Vacaciones').count()
            dias_permiso_con_goce = asistencias.filter(estado='Permiso con goce').count()
            dias_permiso_sin_goce = asistencias.filter(estado='Permiso sin goce').count()
            dias_licencia_medica = asistencias.filter(estado='Licencia Medica').count()
            dias_ausente = asistencias.filter(estado='Ausente').count()
            
            # Días trabajados = todos los días que generan pago
            # (Presente + Descanso + Vacaciones + Permiso con goce + Licencia médica)
            # NO incluye: Ausente, Permiso sin goce
            dias_trabajados = dias_presentes + dias_descanso + dias_vacaciones + dias_permiso_con_goce + dias_licencia_medica
            
            # Calcular salario base del período
            salario_mensual = empleado.salario_base_q or Decimal('0')
            
            # Calcular salario según tipo de período
            if nomina.tipo_periodo == 'MENSUAL':
                salario_periodo = salario_mensual
                dias_periodo = 30
            elif nomina.tipo_periodo == 'QUINCENAL':
                salario_periodo = salario_mensual / Decimal('2')
                dias_periodo = 15
            else:  # SEMANAL
                salario_periodo = salario_mensual / Decimal('4')
                dias_periodo = 7
            
            # Calcular salario por día
            salario_diario = salario_periodo / Decimal(str(dias_periodo)) if dias_periodo > 0 else Decimal('0')
            
            # Días con pago = días trabajados (ya calculado arriba)
            dias_con_pago = dias_trabajados
            
            # Salario base devengado (proporcional a días con pago)
            salario_devengado = salario_diario * Decimal(str(dias_con_pago))
            
            # Calcular horas extra (solo de días Presente con más de 8 horas)
            horas_extra = Decimal('0')
            for asistencia in asistencias.filter(estado='Presente'):
                if asistencia.horas_trabajadas and asistencia.horas_trabajadas > 8:
                    horas_extra += Decimal(str(asistencia.horas_trabajadas - 8))
            
            # Valor hora extra (1.5x hora normal)
            valor_hora = salario_diario / Decimal('8') if salario_diario > 0 else Decimal('0')
            monto_horas_extra = horas_extra * valor_hora * Decimal('1.5')
            
            # Bonificación incentivo (Q250 mensual si salario <= Q3500)
            # Se prorratea según los días con pago del período
            if salario_mensual <= Decimal('3500') and dias_periodo > 0:
                bonificacion_diaria = Decimal('250') / Decimal('30')  # Q250 mensual / 30 días
                bonificaciones = bonificacion_diaria * Decimal(str(dias_con_pago))
            else:
                bonificaciones = Decimal('0')
            
            # Total devengado
            total_devengado = salario_devengado + monto_horas_extra + bonificaciones
            
            # Calcular IGSS (4.83% del salario base devengado, no de bonificaciones)
            igss = salario_devengado * Decimal('0.0483')
            
            # Calcular ISR (simplificado - 5% si gana más de Q4000)
            isr = Decimal('0')
            if total_devengado > Decimal('4000'):
                isr = (total_devengado - Decimal('4000')) * Decimal('0.05')
            
            # Total descuentos
            total_descuentos = igss + isr
            
            # Salario neto
            salario_neto = total_devengado - total_descuentos
            
            # Crear detalle de nómina
            NominaDetalle.objects.create(
                nomina=nomina,
                empleado=empleado,
                dias_trabajados=dias_trabajados,
                dias_descanso=dias_descanso,
                dias_vacaciones=dias_vacaciones,
                dias_permiso_con_goce=dias_permiso_con_goce,
                dias_permiso_sin_goce=dias_permiso_sin_goce,
                dias_licencia_medica=dias_licencia_medica,
                dias_ausente=dias_ausente,
                salario_base_mensual=salario_mensual,
                salario_base_periodo=salario_periodo,
                salario_base_devengado=salario_devengado,
                horas_extra=horas_extra,
                monto_horas_extra=monto_horas_extra,
                bonificaciones=bonificaciones,
                igss=igss,
                isr=isr,
                otros_descuentos=Decimal('0'),
                total_devengado=total_devengado,
                total_descuentos=total_descuentos,
                salario_neto=salario_neto,
                estado='CALCULADO'
            )
        
        # Actualizar estado de la nómina
        nomina.estado = 'CALCULADA'
        nomina.save()

    @action(detail=True, methods=['post'])
    def recalcular(self, request, pk=None):
        """
        Recalcula la nómina eliminando los detalles anteriores
        """
        nomina = self.get_object()
        
        if nomina.estado == 'PAGADA':
            return Response(
                {'error': 'No se puede recalcular una nómina ya pagada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Eliminar detalles anteriores
        nomina.detalles.all().delete()
        
        # Recalcular
        empleados_incluidos = request.data.get('empleadosIncluidos', 'todos')
        self._calcular_nomina(nomina, empleados_incluidos)
        
        serializer = self.get_serializer(nomina)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        """
        Cambia el estado de la nómina
        """
        nomina = self.get_object()
        nuevo_estado = request.data.get('estado', '').upper()
        
        estados_validos = ['ABIERTA', 'CALCULADA', 'CERRADA', 'PAGADA']
        if nuevo_estado not in estados_validos:
            return Response(
                {'error': f'Estado inválido. Estados válidos: {estados_validos}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        nomina.estado = nuevo_estado
        nomina.save()
        
        serializer = self.get_serializer(nomina)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def toggle_activo(self, request, pk=None):
        """
        Activa o desactiva una nómina (soft delete)
        """
        nomina = self.get_object()
        nomina.activo = not nomina.activo
        nomina.save()
        
        # También desactivar/activar los detalles asociados
        nomina.detalles.update(activo=nomina.activo)
        
        serializer = self.get_serializer(nomina)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete - desactiva la nómina en lugar de eliminarla
        """
        nomina = self.get_object()
        nomina.activo = False
        nomina.save()
        
        # También desactivar los detalles asociados
        nomina.detalles.update(activo=False)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Estadísticas generales de nóminas
        """
        queryset = self.get_queryset()
        
        total_nominas = queryset.count()
        nominas_abiertas = queryset.filter(estado='ABIERTA').count()
        nominas_calculadas = queryset.filter(estado='CALCULADA').count()
        nominas_cerradas = queryset.filter(estado='CERRADA').count()
        nominas_pagadas = queryset.filter(estado='PAGADA').count()
        
        # Totales globales
        detalles = NominaDetalle.objects.filter(
            nomina__in=queryset,
            activo=True
        )
        
        totales = detalles.aggregate(
            total_empleados=Count('id'),
            total_devengado=Coalesce(Sum('total_devengado'), Decimal('0')),
            total_descuentos=Coalesce(Sum('total_descuentos'), Decimal('0')),
            total_neto=Coalesce(Sum('salario_neto'), Decimal('0'))
        )
        
        stats = {
            'total_nominas': total_nominas,
            'nominas_abiertas': nominas_abiertas,
            'nominas_calculadas': nominas_calculadas,
            'nominas_cerradas': nominas_cerradas,
            'nominas_pagadas': nominas_pagadas,
            'total_empleados_nomina': totales['total_empleados'],
            'total_devengado_global': totales['total_devengado'],
            'total_descuentos_global': totales['total_descuentos'],
            'total_neto_global': totales['total_neto'],
        }
        
        serializer = NominaStatsSerializer(stats)
        return Response(serializer.data)


class NominaDetalleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para detalles de nómina
    """
    queryset = NominaDetalle.objects.select_related('empleado', 'nomina').all()
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return NominaDetalleListSerializer
        return NominaDetalleSerializer

    def get_queryset(self):
        """
        Filtros opcionales:
        - nomina_id: filtrar por nómina
        - empleado_id: filtrar por empleado
        - pagado: filtrar por estado de pago
        - activo: filtrar solo registros activos
        """
        queryset = self.queryset

        # Filtro por nómina
        nomina_id = self.request.query_params.get('nomina_id', None)
        if nomina_id:
            queryset = queryset.filter(nomina_id=nomina_id)

        # Filtro por empleado
        empleado_id = self.request.query_params.get('empleado_id', None)
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)

        # Filtro por pagado
        pagado = self.request.query_params.get('pagado', None)
        if pagado is not None:
            queryset = queryset.filter(pagado=pagado.lower() == 'true')

        # Filtro por activo
        activo = self.request.query_params.get('activo', 'true')
        if activo.lower() == 'true':
            queryset = queryset.filter(activo=True)
        elif activo.lower() == 'false':
            queryset = queryset.filter(activo=False)

        return queryset.order_by('empleado__codigo_empleado')

    @action(detail=True, methods=['patch'])
    def ajustar(self, request, pk=None):
        """
        Ajusta manualmente los valores del detalle de nómina
        """
        detalle = self.get_object()
        
        if detalle.pagado:
            return Response(
                {'error': 'No se puede ajustar un registro ya pagado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Campos que se pueden ajustar
        campos_ajustables = [
            'bonificaciones', 'otros_descuentos', 'horas_extra',
            'monto_horas_extra', 'observaciones'
        ]
        
        for campo in campos_ajustables:
            valor = request.data.get(campo)
            if valor is not None:
                setattr(detalle, campo, Decimal(str(valor)) if campo != 'observaciones' else valor)
        
        # Recalcular totales
        detalle.total_devengado = (
            detalle.salario_base_devengado + 
            detalle.monto_horas_extra + 
            detalle.bonificaciones
        )
        detalle.total_descuentos = detalle.igss + detalle.isr + detalle.otros_descuentos
        detalle.salario_neto = detalle.total_devengado - detalle.total_descuentos
        detalle.estado = 'AJUSTADO'
        detalle.save()
        
        serializer = self.get_serializer(detalle)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def pagar(self, request, pk=None):
        """
        Marca el detalle como pagado y registra el pago
        """
        detalle = self.get_object()
        
        if detalle.pagado:
            return Response(
                {'error': 'Este registro ya fue pagado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        forma_pago = request.data.get('forma_pago', 'EFECTIVO').upper()
        
        # Crear registro de pago
        pago = PagoNomina.objects.create(
            nomina_detalle=detalle,
            forma_pago=forma_pago,
            monto=detalle.salario_neto,
            usuario=request.user,
            banco=request.data.get('banco'),
            numero_cheque=request.data.get('numero_cheque'),
            cuenta_bancaria=request.data.get('cuenta_bancaria'),
            fecha_cobro=request.data.get('fecha_cobro')
        )
        
        # Actualizar detalle
        detalle.pagado = True
        detalle.metodo_pago = forma_pago
        detalle.fecha_pagado = timezone.now()
        detalle.estado = 'PAGADO'
        detalle.save()
        
        # Verificar si todos los detalles de la nómina están pagados
        nomina = detalle.nomina
        if not nomina.detalles.filter(activo=True, pagado=False).exists():
            nomina.estado = 'PAGADA'
            nomina.save()
        
        serializer = self.get_serializer(detalle)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """
        Cambia el estado a ANULADO (no desactiva el registro)
        """
        detalle = self.get_object()
        motivo = request.data.get('motivo', 'Anulación manual')
        
        if detalle.pagado:
            # Si está pagado, anular los registros de pago
            pagos = PagoNomina.objects.filter(nomina_detalle=detalle, anulado=False)
            for pago in pagos:
                pago.anulado = True
                pago.motivo_anulacion = motivo
                pago.save()
            
            # Limpiar datos de pago
            detalle.pagado = False
            detalle.metodo_pago = None
            detalle.fecha_pagado = None
        
        # Cambiar estado a ANULADO (pero mantener activo=True para que siga visible)
        detalle.estado = 'ANULADO'
        detalle.observaciones = f"{detalle.observaciones or ''}\nAnulado: {motivo}".strip()
        detalle.save()
        
        # Actualizar estado de la nómina si estaba PAGADA
        nomina = detalle.nomina
        if nomina.estado == 'PAGADA':
            nomina.estado = 'CALCULADA'
            nomina.save()
        
        serializer = self.get_serializer(detalle)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def quitar_anulacion(self, request, pk=None):
        """
        Quita la anulación y vuelve a estado CALCULADO (Pendiente)
        """
        detalle = self.get_object()
        
        if detalle.estado != 'ANULADO':
            return Response(
                {'error': 'Este registro no está anulado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Volver a estado CALCULADO (Pendiente)
        detalle.estado = 'CALCULADO'
        detalle.observaciones = f"{detalle.observaciones or ''}\nAnulación removida".strip()
        detalle.save()
        
        serializer = self.get_serializer(detalle)
        return Response(serializer.data)


class PagoNominaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para pagos de nómina
    """
    queryset = PagoNomina.objects.select_related('nomina_detalle__empleado').all()
    serializer_class = PagoNominaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """
        Filtros opcionales:
        - nomina_detalle_id: filtrar por detalle de nómina
        - forma_pago: filtrar por forma de pago
        - anulado: filtrar por estado de anulación
        """
        queryset = self.queryset

        # Filtro por detalle de nómina
        nomina_detalle_id = self.request.query_params.get('nomina_detalle_id', None)
        if nomina_detalle_id:
            queryset = queryset.filter(nomina_detalle_id=nomina_detalle_id)

        # Filtro por forma de pago
        forma_pago = self.request.query_params.get('forma_pago', None)
        if forma_pago:
            queryset = queryset.filter(forma_pago=forma_pago.upper())

        # Filtro por anulado
        anulado = self.request.query_params.get('anulado', None)
        if anulado is not None:
            queryset = queryset.filter(anulado=anulado.lower() == 'true')

        return queryset.order_by('-fecha_pago')

    def perform_create(self, serializer):
        """Asigna el usuario actual al crear el pago"""
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['patch'])
    def anular(self, request, pk=None):
        """
        Anula un pago
        """
        pago = self.get_object()
        
        if pago.anulado:
            return Response(
                {'error': 'Este pago ya está anulado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        motivo = request.data.get('motivo', 'Sin motivo especificado')
        
        pago.anulado = True
        pago.motivo_anulacion = motivo
        pago.save()
        
        # Actualizar estado del detalle
        detalle = pago.nomina_detalle
        detalle.pagado = False
        detalle.metodo_pago = None
        detalle.fecha_pagado = None
        detalle.estado = 'CALCULADO'
        detalle.save()
        
        # Actualizar estado de la nómina
        nomina = detalle.nomina
        if nomina.estado == 'PAGADA':
            nomina.estado = 'CERRADA'
            nomina.save()
        
        serializer = self.get_serializer(pago)
        return Response(serializer.data)
