from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MovimientoCaja, MovimientoCajaDetalle
from .serializers import MovimientoCajaSerializer, MovimientoCajaDetalleSerializer


class MovimientoCajaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para movimientos de caja
    """
    queryset = MovimientoCaja.objects.all()
    serializer_class = MovimientoCajaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['empresa', 'tipo', 'estado']
    search_fields = ['referencia', 'descripcion']
    ordering_fields = ['fecha_hora', 'total', 'created_at']
    ordering = ['-fecha_hora']


class MovimientoCajaDetalleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para detalles de movimientos de caja
    """
    queryset = MovimientoCajaDetalle.objects.all()
    serializer_class = MovimientoCajaDetalleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['movimiento']
