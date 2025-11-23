from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Empleado
from .serializers import (
    EmpleadoSerializer,
    EmpleadoListSerializer,
    EmpleadosStatsSerializer
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
