"""
Views para Zona
Responsabilidad: CRUD y acciones sobre zonas
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from apps.eventos.models import Evento, Zona
from apps.eventos.serializers import ZonaSerializer, ZonaListSerializer
from config.hashid_utils import decode_id


class ZonaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Zonas
    Responsabilidad: CRUD de zonas con consultas de disponibilidad
    """
    queryset = Zona.objects.select_related('evento').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion', 'evento__nombre']
    
    def get_object(self):
        """Permitir búsqueda por ID o encoded_id"""
        lookup_value = self.kwargs.get('pk')
        decoded_id = decode_id(lookup_value)
        
        if decoded_id:
            return get_object_or_404(self.queryset, pk=decoded_id)
        
        try:
            return get_object_or_404(self.queryset, pk=int(lookup_value))
        except (ValueError, TypeError):
            return super().get_object()
    
    def get_permissions(self):
        """Permisos según acción - público para consultas, autenticado para cambios"""
        if self.action in ['list', 'retrieve', 'zonas_disponibles']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Seleccionar serializer según acción"""
        if self.action == 'list':
            return ZonaListSerializer
        return ZonaSerializer
    
    def get_queryset(self):
        """Filtrar zonas por evento si se proporciona"""
        queryset = super().get_queryset()
        evento_id = self.request.query_params.get('evento_id')
        
        if evento_id:
            decoded_id = decode_id(evento_id)
            lookup_id = decoded_id if decoded_id else evento_id
            queryset = queryset.filter(evento_id=lookup_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def zonas_disponibles(self, request):
        """
        Obtener solo las zonas con disponibilidad
        
        Parámetros:
            - evento_id: ID del evento (requerido) o encoded_id
            - debug: Si es '1', devuelve información de debug
        """
        evento_id = request.query_params.get('evento_id')
        
        if not evento_id:
            return Response(
                {'error': 'evento_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Decodificar ID
        decoded_id = decode_id(evento_id)
        lookup_id = decoded_id if decoded_id else evento_id
        
        try:
            evento = Evento.objects.get(id=lookup_id, activo=True)
        except Evento.DoesNotExist:
            return Response(
                {'error': 'Evento no encontrado o no está activo'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener zonas activas
        todas_zonas = Zona.objects.filter(evento=evento)
        zonas_activas = todas_zonas.filter(activo=True)
        
        # Información de debug
        debug_info = self._generar_debug_info(evento, todas_zonas, zonas_activas)
        
        # Filtrar zonas con disponibilidad
        zonas_con_stock = [
            zona for zona in zonas_activas 
            if zona.tiene_disponibilidad()
        ]
        
        serializer = ZonaListSerializer(zonas_con_stock, many=True)
        
        # Responder con o sin debug
        if request.query_params.get('debug') == '1':
            return Response({
                'debug': debug_info,
                'zonas': serializer.data
            })
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def disponibilidad(self, request, pk=None):
        """Verificar disponibilidad de una zona"""
        zona = self.get_object()
        cantidad = int(request.query_params.get('cantidad', 1))
        
        return Response({
            'zona': zona.nombre,
            'disponible': zona.tiene_disponibilidad(cantidad),
            'tickets_disponibles': zona.tickets_disponibles(),
            'tickets_solicitados': cantidad
        })
    
    # Método privado auxiliar
    
    def _generar_debug_info(self, evento, todas_zonas, zonas_activas):
        """Generar información de debug para zonas"""
        debug_info = {
            'evento_id': evento.id,
            'evento_nombre': evento.nombre,
            'evento_estado': evento.estado,
            'evento_activo': evento.activo,
            'total_zonas': todas_zonas.count(),
            'zonas_activas': zonas_activas.count(),
            'zonas_info': []
        }
        
        for zona in zonas_activas:
            debug_info['zonas_info'].append({
                'id': zona.id,
                'nombre': zona.nombre,
                'activo': zona.activo,
                'capacidad_maxima': zona.capacidad_maxima,
                'tickets_vendidos': zona.tickets_vendidos(),
                'tickets_disponibles': zona.tickets_disponibles(),
                'tiene_disponibilidad': zona.tiene_disponibilidad()
            })
        
        return debug_info
