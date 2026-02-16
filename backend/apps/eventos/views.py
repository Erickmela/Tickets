"""
Views para Eventos y Zonas
Aplicando Single Responsibility y encapsulación
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Evento, Zona
from .serializers import (
    EventoSerializer, EventoListSerializer, EventoCreateSerializer,
    ZonaSerializer, ZonaListSerializer
)


class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Eventos
    Responsabilidad: CRUD de eventos
    """
    queryset = Evento.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion', 'lugar']
    
    def get_serializer_class(self):
        """Seleccionar serializer según acción"""
        if self.action == 'list':
            return EventoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EventoCreateSerializer
        return EventoSerializer
    
    @action(detail=False, methods=['get'])
    def evento_activo(self, request):
        """
        Obtener el evento activo actual (endpoint legacy)
        DEPRECATED: Use eventos_activos para obtener todos los eventos activos
        """
        try:
            evento = Evento.objects.get(activo=True)
            serializer = EventoSerializer(evento)
            return Response(serializer.data)
        except Evento.DoesNotExist:
            return Response(
                {'message': 'No hay eventos activos'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Evento.MultipleObjectsReturned:
            # Si hay múltiples eventos activos, devolver el primero
            evento = Evento.objects.filter(activo=True).first()
            serializer = EventoSerializer(evento)
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def eventos_activos(self, request):
        """
        Obtener todos los eventos activos
        Permite múltiples eventos activos para diferentes lugares o fechas
        """
        eventos = Evento.objects.filter(activo=True).order_by('-fecha', 'nombre')
        if not eventos.exists():
            return Response(
                {'message': 'No hay eventos activos'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EventoSerializer(eventos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar un evento (desactivando los demás)"""
        evento = self.get_object()
        # Desactivar todos los eventos
        Evento.objects.update(activo=False)
        # Activar este evento
        evento.activo = True
        evento.save()
        return Response({'status': 'Evento activado correctamente'})
    
    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Obtener estadísticas completas del evento para el dashboard"""
        from django.db.models import Sum, Count, Q
        from apps.ventas.models import Venta, Ticket, EstadoTicket, MetodoPago
        
        evento = self.get_object()
        
        # Obtener todos los tickets del evento
        tickets_evento = Ticket.objects.filter(zona__evento=evento)
        
        # Estadísticas generales de tickets
        total_tickets_vendidos = tickets_evento.filter(estado=EstadoTicket.ACTIVO).count()
        tickets_usados = tickets_evento.filter(estado=EstadoTicket.USADO).count()
        tickets_anulados = tickets_evento.filter(estado=EstadoTicket.ANULADO).count()
        
        # Estadísticas de ventas
        ventas_evento = Venta.objects.filter(
            tickets__zona__evento=evento,
            activo=True
        ).distinct()
        
        total_ventas = ventas_evento.count()
        ingresos_totales = ventas_evento.aggregate(
            total=Sum('total_pagado')
        )['total'] or 0
        
        # Ventas por método de pago
        ventas_por_metodo = []
        for metodo_code, metodo_label in MetodoPago.choices:
            ventas_metodo = ventas_evento.filter(metodo_pago=metodo_code)
            monto = ventas_metodo.aggregate(total=Sum('total_pagado'))['total'] or 0
            if ventas_metodo.exists():
                ventas_por_metodo.append({
                    'metodo': metodo_label,
                    'cantidad_ventas': ventas_metodo.count(),
                    'monto_total': float(monto)
                })
        
        # Estadísticas por zona
        zonas_stats = []
        for zona in evento.zonas.all():
            tickets_zona = tickets_evento.filter(zona=zona, estado=EstadoTicket.ACTIVO)
            ingresos_zona = tickets_zona.count() * zona.precio
            
            zonas_stats.append({
                'id': zona.id,
                'nombre': zona.nombre,
                'precio': float(zona.precio),
                'capacidad_maxima': zona.capacidad_maxima,
                'tickets_vendidos': zona.tickets_vendidos(),
                'tickets_disponibles': zona.tickets_disponibles(),
                'porcentaje_ocupacion': zona.porcentaje_ocupacion(),
                'ingresos': float(ingresos_zona)
            })
        
        # Ordenar zonas por ingresos (mayor a menor)
        zonas_stats.sort(key=lambda x: x['ingresos'], reverse=True)
        
        return Response({
            'evento': {
                'id': evento.id,
                'nombre': evento.nombre,
                'fecha': evento.fecha,
                'lugar': evento.lugar,
                'estado': evento.get_estado_display()
            },
            'capacidad': {
                'total': evento.capacidad_total(),
                'vendidos': total_tickets_vendidos,
                'disponibles': evento.capacidad_total() - total_tickets_vendidos,
                'porcentaje_ocupacion': round((total_tickets_vendidos / evento.capacidad_total() * 100) if evento.capacidad_total() > 0 else 0, 2)
            },
            'tickets': {
                'total_vendidos': total_tickets_vendidos,
                'activos': total_tickets_vendidos,
                'usados': tickets_usados,
                'anulados': tickets_anulados
            },
            'ventas': {
                'total_ventas': total_ventas,
                'ingresos_totales': float(ingresos_totales),
                'promedio_venta': float(ingresos_totales / total_ventas) if total_ventas > 0 else 0,
                'por_metodo_pago': ventas_por_metodo
            },
            'zonas': zonas_stats
        })


class ZonaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Zonas
    Responsabilidad: CRUD de zonas
    """
    queryset = Zona.objects.select_related('evento').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion', 'evento__nombre']
    
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
            queryset = queryset.filter(evento_id=evento_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def zonas_disponibles(self, request):
        """
        Obtener solo las zonas con disponibilidad
        Parámetros:
            - evento_id: ID del evento (requerido)
            - debug: Si es '1', devuelve información de debug
        """
        evento_id = request.query_params.get('evento_id')
        
        if not evento_id:
            return Response(
                {'error': 'evento_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            evento = Evento.objects.get(id=evento_id, activo=True)
        except Evento.DoesNotExist:
            return Response(
                {'error': 'Evento no encontrado o no está activo'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener todas las zonas del evento
        todas_zonas = Zona.objects.filter(evento=evento)
        zonas_activas = todas_zonas.filter(activo=True)
        
        # Debug info
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
            zona_info = {
                'id': zona.id,
                'nombre': zona.nombre,
                'activo': zona.activo,
                'capacidad_maxima': zona.capacidad_maxima,
                'tickets_vendidos': zona.tickets_vendidos(),
                'tickets_disponibles': zona.tickets_disponibles(),
                'tiene_disponibilidad': zona.tiene_disponibilidad()
            }
            debug_info['zonas_info'].append(zona_info)
        
        # Filtrar zonas con disponibilidad
        zonas_con_stock = [
            zona for zona in zonas_activas 
            if zona.tiene_disponibilidad()
        ]
        
        serializer = ZonaListSerializer(zonas_con_stock, many=True)
        
        # Agregar debug info si se solicita
        response_data = serializer.data
        if request.query_params.get('debug') == '1':
            return Response({
                'debug': debug_info,
                'zonas': response_data
            })
        
        return Response(response_data)
    
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
