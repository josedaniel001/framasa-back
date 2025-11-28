# Views del módulo Taller

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Maquinaria, TipoMaquinaria, EmpresaMaquinaria
from .serializers import MaquinariaSerializer, MaquinariaListSerializer


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
