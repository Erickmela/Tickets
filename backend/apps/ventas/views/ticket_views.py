"""
Views para Ticket
Responsabilidad: Consulta de tickets (read-only)
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.ventas.models import Ticket
from apps.ventas.serializers import TicketSerializer, TicketListSerializer


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta de Tickets
    Responsabilidad: Solo lectura de tickets
    """
    queryset = Ticket.objects.select_related('zona__evento').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['dni_titular', 'nombre_titular', 'codigo_uuid']
    
    def get_serializer_class(self):
        """Seleccionar serializer según acción"""
        if self.action == 'list':
            return TicketListSerializer
        return TicketSerializer
    
    def get_queryset(self):
        """Aplicar filtros adicionales"""
        queryset = super().get_queryset()
        
        # Filtrar por estado si se proporciona
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def por_evento(self, request):
        """Obtener tickets de un evento específico"""
        evento_id = request.query_params.get('evento_id')
        if not evento_id:
            return Response(
                {'error': 'evento_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tickets = Ticket.objects.filter(zona__evento_id=evento_id)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_dni(self, request):
        """Buscar tickets por DNI del titular"""
        dni = request.query_params.get('dni')
        if not dni:
            return Response(
                {'error': 'dni es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tickets = Ticket.objects.filter(dni_titular=dni)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
