"""
Views para Zona
Responsabilidad: CRUD y acciones sobre zonas
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from apps.eventos.models import Evento, Zona, Presentacion
from apps.eventos.serializers import ZonaSerializer, ZonaListSerializer



class ZonaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Zonas
    Responsabilidad: CRUD de zonas con consultas de disponibilidad
    Optimizado con select_related para evitar N+1 queries
    """
    queryset = Zona.objects.select_related(
        'presentacion__evento'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion', 'presentacion__evento__nombre']
    lookup_field = 'codigo'  # Usar código UUID en lugar de ID numérico
    
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
        presentacion_id = self.request.query_params.get('presentacion_id')
        
        if evento_id:
            # Filtrar por todas las presentaciones del evento
            queryset = queryset.filter(presentacion__evento_id=evento_id)
        
        if presentacion_id:
            # Filtrar por presentación específica
            queryset = queryset.filter(presentacion_id=presentacion_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def zonas_disponibles(self, request):
        """
        Obtener solo las zonas con disponibilidad de todas las presentaciones de un evento
        """
        evento_id = request.query_params.get('evento_id')
        presentacion_id = request.query_params.get('presentacion_id')
        
        if not evento_id:
            return Response(
                {'error': 'evento_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            evento = Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return Response(
                {'error': 'Evento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Filtrar zonas de las presentaciones del evento
        if presentacion_id:
            # Filtrar por presentación específica
            todas_zonas = Zona.objects.filter(
                presentacion__evento=evento,
                presentacion_id=presentacion_id
            )
        else:
            # Todas las zonas de todas las presentaciones del evento
            todas_zonas = Zona.objects.filter(presentacion__evento=evento)
        
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
