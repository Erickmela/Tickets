"""
Views para Evento
Responsabilidad: CRUD y acciones sobre eventos
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Min
from django.utils import timezone
from datetime import timedelta

from apps.eventos.models import Evento, Zona
from apps.eventos.serializers import (
    EventoSerializer, 
    EventoListSerializer, 
    EventoCreateSerializer,
    EventoSelectSerializer
)
from apps.ventas.models import Venta, Ticket, EstadoTicket, MetodoPago
from config.hashid_utils import decode_id


class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Eventos
    Responsabilidad: CRUD de eventos con endpoints especializados
    """
    queryset = Evento.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion', 'lugar']
    
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
        if self.action in ['list', 'retrieve', 'evento_activo', 'eventos_activos']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
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
            evento = Evento.objects.filter(activo=True).first()
            serializer = EventoSerializer(evento)
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def eventos_activos(self, request):
        """Obtener eventos próximos y activos (estado 1 o 2)"""
        # Filtrar por estado '1' (Próximo) o '2' (Activo)
        eventos = Evento.objects.filter(estado__in=['1', '2']).annotate(
            primera_fecha=Min('presentaciones__fecha')
        ).order_by('-primera_fecha', 'nombre')
        
        if not eventos.exists():
            return Response(
                {'message': 'No hay eventos próximos o activos'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EventoSerializer(eventos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='select')
    def select_options(self, request):
        """
        Endpoint optimizado para selects
        Retorna solo: id, encoded_id, nombre
        Filtra solo eventos activos/próximos (estado 1 o 2)
        """
        eventos = Evento.objects.filter(
            estado__in=['1', '2']
        ).annotate(
            primera_fecha=Min('presentaciones__fecha')
        ).order_by('nombre')
        
        serializer = EventoSelectSerializer(eventos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar un evento"""
        evento = self.get_object()
        evento.estado = '2'  # ACTIVO
        evento.activo = True
        evento.save()
        return Response({'status': 'Evento activado correctamente'})
    
    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Obtener estadísticas completas del evento para el dashboard"""
        evento = self.get_object()
        
        # Tickets del evento
        tickets_evento = Ticket.objects.filter(zona__evento=evento)
        total_tickets_vendidos = tickets_evento.filter(estado=EstadoTicket.ACTIVO).count()
        tickets_usados = tickets_evento.filter(estado=EstadoTicket.USADO).count()
        tickets_anulados = tickets_evento.filter(estado=EstadoTicket.ANULADO).count()
        
        # Ventas del evento
        ventas_evento = Venta.objects.filter(
            tickets__zona__evento=evento,
            activo=True
        ).distinct()
        
        total_ventas = ventas_evento.count()
        ingresos_totales = ventas_evento.aggregate(total=Sum('total_pagado'))['total'] or 0
        
        # Ventas por método de pago
        ventas_por_metodo = self._calcular_ventas_por_metodo(ventas_evento)
        
        # Estadísticas por zona
        zonas_stats = self._calcular_estadisticas_zonas(evento, tickets_evento)
        
        return Response({
            'evento': {
                'id': evento.id,
                'nombre': evento.nombre,
                'lugar': evento.lugar,
                'estado': evento.get_estado_display()
            },
            'capacidad': {
                'total': evento.capacidad_total(),
                'vendidos': total_tickets_vendidos,
                'disponibles': evento.capacidad_total() - total_tickets_vendidos,
                'porcentaje_ocupacion': round(
                    (total_tickets_vendidos / evento.capacidad_total() * 100) 
                    if evento.capacidad_total() > 0 else 0, 2
                )
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
    
    @action(detail=True, methods=['get'])
    def evolucion_ventas(self, request, pk=None):
        """Obtener evolución de ventas de los últimos N días"""
        evento = self.get_object()
        dias = int(request.query_params.get('dias', 7))
        
        fecha_fin = timezone.now()
        fecha_inicio = fecha_fin - timedelta(days=dias)
        
        ventas = Venta.objects.filter(
            tickets__zona__evento=evento,
            activo=True,
            fecha_venta__gte=fecha_inicio,
            fecha_venta__lte=fecha_fin
        ).distinct()
        
        evolucion = []
        for i in range(dias):
            fecha = fecha_inicio + timedelta(days=i)
            fecha_str = fecha.strftime('%d %b')
            
            ventas_dia = ventas.filter(fecha_venta__date=fecha.date())
            total_ventas_dia = ventas_dia.count()
            ingresos_dia = ventas_dia.aggregate(total=Sum('total_pagado'))['total'] or 0
            
            evolucion.append({
                'fecha': fecha_str,
                'ventas': total_ventas_dia,
                'ingresos': float(ingresos_dia)
            })
        
        return Response(evolucion)
    
    @action(detail=True, methods=['get'])
    def tickets_reporte(self, request, pk=None):
        """Obtener todos los tickets del evento para generar reporte"""
        evento = self.get_object()
        
        tickets = Ticket.objects.filter(
            zona__evento=evento
        ).select_related('zona', 'venta').order_by('zona__nombre', 'nombre_titular')
        
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'codigo_uuid': str(ticket.codigo_uuid),
                'token_qr': ticket.token_encriptado,
                'qr_image_url': ticket.qr_image.url if ticket.qr_image else None,
                'nombre_titular': ticket.nombre_titular,
                'dni_titular': ticket.dni_titular,
                'zona': ticket.zona.nombre,
                'precio': float(ticket.zona.precio),
                'estado': ticket.estado,
                'fecha_compra': ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M')
            })
        
        # Obtener la primera presentación si existe
        primera_presentacion = evento.presentaciones.first()
        
        return Response({
            'evento': {
                'nombre': evento.nombre,
                'fecha': primera_presentacion.fecha.strftime('%d/%m/%Y') if primera_presentacion else '-',
                'hora_inicio': primera_presentacion.hora_inicio.strftime('%H:%M') if primera_presentacion else '-',
                'lugar': evento.lugar,
                'region': evento.region or '-'
            },
            'tickets': tickets_data,
            'total_tickets': len(tickets_data)
        })
    
    @action(detail=True, methods=['get'], url_path='presentaciones')
    def presentaciones_evento(self, request, pk=None):
        """
        Obtener presentaciones de un evento
        GET /api/eventos/{evento_id}/presentaciones/
        """
        evento = self.get_object()
        from apps.eventos.models import Presentacion
        
        presentaciones = Presentacion.objects.filter(
            evento=evento
        ).order_by('fecha', 'hora_inicio')
        
        data = [{
            'id': p.id,
            'fecha': p.fecha,
            'hora_inicio': p.hora_inicio,
            'nombre_display': f"{p.fecha} - {p.hora_inicio}" if p.fecha else f"Presentación #{p.id}"
        } for p in presentaciones]
        
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='presentaciones/(?P<presentacion_id>[^/.]+)/zonas')
    def zonas_presentacion(self, request, presentacion_id=None):
        """
        Obtener zonas de una presentación
        """
        from apps.eventos.models import Presentacion, Zona
        
        presentacion = get_object_or_404(Presentacion, id=presentacion_id)
        zonas = Zona.objects.filter(
            presentacion=presentacion,
            activo=True
        ).order_by('nombre')
        
        data = [{
            'id': z.id,
            'nombre': z.nombre,
            'precio': float(z.precio),
            'capacidad_maxima': z.capacidad_maxima,
            'tickets_vendidos': z.tickets_vendidos(),
            'tickets_disponibles': z.tickets_disponibles(),
            'tiene_disponibilidad': z.tiene_disponibilidad()
        } for z in zonas]
        
        return Response(data)
    
    # Métodos privados auxiliares
    
    def _calcular_ventas_por_metodo(self, ventas_evento):
        """Calcular ventas agrupadas por método de pago"""
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
        return ventas_por_metodo
    
    def _calcular_estadisticas_zonas(self, evento, tickets_evento):
        """Calcular estadísticas por zona"""
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
        
        # Ordenar por ingresos (mayor a menor)
        zonas_stats.sort(key=lambda x: x['ingresos'], reverse=True)
        return zonas_stats
